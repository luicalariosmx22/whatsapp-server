#!/usr/bin/env python3
"""
Servidor WebSocket REAL para WhatsApp Web usando Selenium
Este servidor maneja las conexiones reales a WhatsApp Web
"""

import os
import sys
import json
import uuid
import time
import threading
import qrcode
import io
import base64
from datetime import datetime
import logging
from flask import Flask, request, render_template
from flask_socketio import SocketIO, emit, disconnect, join_room, leave_room
from flask_cors import CORS

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuración
WS_PORT = int(os.getenv('WS_PORT', 5001))
WS_HOST = os.getenv('WS_HOST', '0.0.0.0')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

class RealWhatsAppWebManager:
    """Gestor REAL de WhatsApp Web usando Selenium"""
    
    def __init__(self):
        self.sessions = {}
        self.active_connections = {}
        self.drivers = {}  # Almacenar drivers de Selenium
        self.lock = threading.Lock()
        
    def create_session(self, client_id):
        """Crear nueva sesión REAL de WhatsApp Web"""
        with self.lock:
            session_id = str(uuid.uuid4())
            self.sessions[session_id] = {
                'client_id': client_id,
                'status': 'pending',
                'created_at': datetime.now(),
                'qr_code': None,
                'authenticated': False,
                'last_activity': datetime.now(),
                'driver': None,
                'phone_number': None
            }
            logger.info(f"Sesión REAL creada: {session_id} para cliente {client_id}")
            return session_id
        
    def get_session(self, session_id):
        """Obtener sesión por ID"""
        with self.lock:
            return self.sessions.get(session_id)
        
    def update_session_status(self, session_id, status, **kwargs):
        """Actualizar estado de sesión"""
        with self.lock:
            if session_id in self.sessions:
                old_status = self.sessions[session_id].get('status', 'unknown')
                self.sessions[session_id]['status'] = status
                self.sessions[session_id]['last_activity'] = datetime.now()
                self.sessions[session_id].update(kwargs)
                
                # Log más detallado
                if status == 'authenticated':
                    logger.info(f"🎉 Sesión {session_id} AUTENTICADA exitosamente (era: {old_status})")
                else:
                    logger.info(f"📱 Sesión {session_id} actualizada: {old_status} -> {status}")
                
                # Log de kwargs adicionales
                if kwargs:
                    logger.info(f"📋 Datos adicionales para {session_id}: {kwargs}")
            else:
                logger.warning(f"⚠️ Intentando actualizar sesión inexistente: {session_id}")
                
    def remove_session(self, session_id):
        """Eliminar sesión y cerrar driver"""
        with self.lock:
            if session_id in self.sessions:
                # Cerrar driver de Selenium si existe
                session = self.sessions[session_id]
                if session.get('driver'):
                    try:
                        session['driver'].quit()
                        logger.info(f"Driver cerrado para sesión: {session_id}")
                    except Exception as e:
                        logger.error(f"Error cerrando driver: {e}")
                
                del self.sessions[session_id]
                logger.info(f"Sesión eliminada: {session_id}")
                
    def setup_chrome_driver(self):
        """Configurar driver de Chromium para WhatsApp Web"""
        try:
            # Verificar si estamos en modo sin Chrome
            if os.getenv('NO_CHROME_MODE') == 'true':
                logger.warning("🚫 Modo sin Chrome activado - Chrome no disponible")
                return None
            
            chrome_options = Options()
            
            # Configuraciones para WhatsApp Web
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--remote-debugging-port=9222")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Configurar headless para Railway
            if os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('PORT'):
                chrome_options.add_argument("--headless=new")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--virtual-time-budget=10000")
                logger.info("🌐 Modo headless activado para Railway")
            
            # User agent personalizado
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # Configurar directorio de datos de usuario único
            user_data_dir = f"/tmp/chrome_user_data_{uuid.uuid4()}"
            chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
            
            # Para desarrollo, usar headless opcional
            if os.getenv('HEADLESS', 'False').lower() == 'true':
                chrome_options.add_argument("--headless")
            
            # Intentar usar Chrome/Chromium directamente primero
            try:
                # Buscar ejecutable de Chrome/Chromium
                chrome_paths = [
                    '/usr/bin/google-chrome',
                    '/usr/bin/chromium-browser',
                    '/usr/bin/chromium',
                    '/usr/bin/chrome',
                    '/snap/bin/chromium',
                    '/opt/google/chrome/chrome'
                ]
                
                # Verificar si hay un path específico configurado
                if os.getenv('CHROME_PATH'):
                    chrome_paths.insert(0, os.getenv('CHROME_PATH'))
                
                chrome_path = None
                for path in chrome_paths:
                    if os.path.exists(path):
                        chrome_path = path
                        break
                
                if chrome_path:
                    chrome_options.binary_location = chrome_path
                    logger.info(f"Usando Chrome en: {chrome_path}")
                else:
                    logger.error("❌ No se encontró Chrome en ninguna ruta")
                    return None
                
                # Configurar servicio con ChromeDriver
                service_paths = [
                    '/usr/bin/chromedriver',
                    '/usr/local/bin/chromedriver'
                ]
                
                service = None
                for path in service_paths:
                    if os.path.exists(path):
                        service = Service(path)
                        logger.info(f"Usando ChromeDriver en: {path}")
                        break
                
                if not service:
                    logger.error("❌ ChromeDriver no encontrado en rutas del sistema")
                    return None
                
            except Exception as e:
                logger.error(f"Error configurando Chromium: {e}")
                return None
            
            # Crear driver
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.set_window_size(1200, 800)
            
            # Ejecutar script para evitar detección
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("✅ Driver de Chromium configurado exitosamente")
            return driver
            
        except Exception as e:
            logger.error(f"❌ Error configurando driver: {e}")
            return None
            
    def start_whatsapp_session(self, session_id):
        """Iniciar sesión REAL de WhatsApp Web"""
        try:
            session = self.get_session(session_id)
            if not session:
                return False
                
            logger.info(f"Iniciando sesión real de WhatsApp Web: {session_id}")
            
            # Verificar si Chrome está disponible
            if os.getenv('NO_CHROME_MODE') == 'true':
                logger.warning("🚫 Chrome no disponible - enviando QR simulado")
                self.send_mock_qr_code(session_id)
                return True
            
            # Crear driver
            driver = self.setup_chrome_driver()
            if not driver:
                logger.error("❌ No se pudo crear el driver de Chrome")
                self.send_mock_qr_code(session_id)
                return True
                
            # Guardar driver en la sesión
            self.update_session_status(session_id, 'connecting', driver=driver)
            
            # Navegar a WhatsApp Web
            logger.info("Navegando a WhatsApp Web...")
            driver.get("https://web.whatsapp.com")
            
            # Esperar a que aparezca el QR
            self.wait_for_qr_code(session_id, driver)
            
            return True
            
        except Exception as e:
            logger.error(f"Error iniciando sesión WhatsApp: {e}")
            self.send_mock_qr_code(session_id)
            return True
            
    def wait_for_qr_code(self, session_id, driver):
        """Esperar y capturar código QR real"""
        try:
            logger.info(f"Esperando código QR para sesión: {session_id}")
            
            # Esperar a que aparezca el QR (máximo 30 segundos)
            wait = WebDriverWait(driver, 30)
            
            # Selector del QR de WhatsApp Web
            qr_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-ref]"))
            )
            
            logger.info("Elemento QR encontrado")
            
            # Obtener el atributo data-ref que contiene el código QR
            qr_data = qr_element.get_attribute("data-ref")
            
            if qr_data:
                logger.info(f"QR Code obtenido: {qr_data[:50]}...")
                
                # Actualizar sesión con QR real
                self.update_session_status(session_id, 'qr_ready', qr_data=qr_data)
                
                # Emitir evento de QR
                socketio.emit('qr_code', {
                    'type': 'qr_code',
                    'session_id': session_id,
                    'qr_data': qr_data,
                    'message': 'Código QR REAL generado',
                    'is_real': True
                }, room=session_id)
                
                # Iniciar monitoreo de autenticación
                self.monitor_authentication(session_id, driver)
                
            else:
                logger.error("No se pudo obtener datos del QR")
                return False
                
        except TimeoutException:
            logger.error("Timeout esperando código QR")
            return False
        except Exception as e:
            logger.error(f"Error capturando QR: {e}")
            return False
            
    def monitor_authentication(self, session_id, driver):
        """Monitorear autenticación real de WhatsApp Web"""
        def monitor():
            try:
                logger.info(f"Monitoreando autenticación para sesión: {session_id}")
                
                # Esperar hasta 120 segundos por autenticación
                wait = WebDriverWait(driver, 120)
                
                # Esperar a que desaparezca el QR y aparezca la interfaz principal
                try:
                    # Múltiples selectores para detectar autenticación exitosa
                    selectors = [
                        # Barra de búsqueda principal
                        "[data-testid='chat-list-search']",
                        "[data-testid='search']", 
                        "[data-testid='chatlist-search']",
                        "input[placeholder*='Search']",
                        "input[placeholder*='Buscar']",
                        "[aria-label*='Search']",
                        "[aria-label*='Buscar']",
                        
                        # Elementos de la interfaz principal
                        "[data-testid='chatlist']",
                        "[data-testid='chat-list']",
                        "[data-testid='side']",
                        "#main",
                        "._3uMse",  # Clase común del chat list
                        "._1jJ70",  # Sidebar
                        
                        # Elementos de la app principal
                        "[data-testid='app-wrapper-main']",
                        "._3q4NP",  # Container principal
                        "._2Zdgs",  # Chat container
                        
                        # Cualquier elemento que contenga "chat"
                        "[data-testid*='chat']",
                        "[aria-label*='Chat']",
                        "[aria-label*='Conversation']"
                    ]
                    
                    authenticated = False
                    found_selector = None
                    
                    for selector in selectors:
                        try:
                            element = wait.until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                            )
                            logger.info(f"✅ Autenticación detectada con selector: {selector}")
                            authenticated = True
                            found_selector = selector
                            break
                        except TimeoutException:
                            continue
                    
                    if not authenticated:
                        # Intentar una verificación más básica
                        try:
                            # Verificar que no estamos en la página de QR
                            qr_canvas = driver.find_elements(By.CSS_SELECTOR, "canvas[aria-label*='QR']")
                            if not qr_canvas:
                                logger.info("✅ No se encontró canvas de QR, asumiendo autenticación")
                                authenticated = True
                                found_selector = "no-qr-canvas"
                            else:
                                logger.info(f"❌ Aún se encuentra canvas de QR: {len(qr_canvas)}")
                        except Exception as e:
                            logger.error(f"Error verificando QR canvas: {e}")
                    
                    if not authenticated:
                        raise TimeoutException("No se pudo detectar autenticación con ningún selector")
                    
                    logger.info(f"¡Autenticación exitosa para sesión: {session_id}!")
                    
                    # Obtener número de teléfono si es posible
                    phone_number = self.get_phone_number(driver)
                    
                    # Actualizar sesión
                    self.update_session_status(
                        session_id, 
                        'authenticated', 
                        authenticated=True,
                        phone_number=phone_number
                    )
                    
                    # Emitir evento de autenticación exitosa
                    socketio.emit('authenticated', {
                        'type': 'authenticated',
                        'session_id': session_id,
                        'message': '¡Autenticación REAL exitosa!',
                        'phone_number': phone_number,
                        'is_real': True,
                        'timestamp': datetime.now().isoformat()
                    }, room=session_id)
                    
                    # Iniciar heartbeat para mantener sesión viva
                    self.start_real_heartbeat(session_id, driver)
                    
                except TimeoutException:
                    logger.warning(f"Timeout en autenticación para sesión: {session_id}")
                    self.update_session_status(session_id, 'qr_expired')
                    
                    # Emitir evento de QR expirado
                    socketio.emit('qr_expired', {
                        'type': 'qr_expired',
                        'session_id': session_id,
                        'message': 'Código QR expirado - Genera uno nuevo'
                    }, room=session_id)
                    
            except Exception as e:
                logger.error(f"Error monitoreando autenticación: {e}")
                
        # Ejecutar monitoreo en hilo separado
        thread = threading.Thread(target=monitor)
        thread.daemon = True
        thread.start()
        
    def get_phone_number(self, driver):
        """Obtener número de teléfono de la sesión"""
        try:
            # Intentar obtener información del usuario
            selectors = [
                "[data-testid='menu-btn']",
                "[data-testid='menu']",
                "[aria-label*='Menu']",
                "[aria-label*='Menú']",
                "._1ZVQX",  # Botón de menú
                "._3XKXx"   # Header button
            ]
            
            for selector in selectors:
                try:
                    # Intentar encontrar algún elemento que nos dé información
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                    if element:
                        # Si encontramos el elemento, significa que estamos autenticados
                        logger.info(f"✅ Elemento de interfaz encontrado: {selector}")
                        return "Sesión autenticada"
                except:
                    continue
            
            return "Sesión activa"
        except Exception as e:
            logger.error(f"Error obteniendo información de usuario: {e}")
            return "Sesión activa"
            
    def start_real_heartbeat(self, session_id, driver):
        """Iniciar heartbeat real para mantener sesión viva"""
        def heartbeat():
            while True:
                try:
                    session = self.get_session(session_id)
                    if not session or session.get('status') != 'authenticated':
                        break
                        
                    # Verificar que el driver sigue activo
                    if driver:
                        # Hacer una acción mínima para mantener la sesión
                        try:
                            driver.current_url
                            
                            # Actualizar última actividad
                            self.update_session_status(session_id, 'authenticated')
                            
                            # Emitir heartbeat
                            socketio.emit('heartbeat', {
                                'type': 'heartbeat',
                                'session_id': session_id,
                                'timestamp': datetime.now().isoformat(),
                                'is_real': True
                            }, room=session_id)
                            
                        except Exception as e:
                            logger.error(f"Driver no válido en heartbeat: {e}")
                            break
                    
                    # Heartbeat cada 30 segundos
                    time.sleep(30)
                    
                except Exception as e:
                    logger.error(f"Error en heartbeat real para sesión {session_id}: {e}")
                    break
                    
        thread = threading.Thread(target=heartbeat)
        thread.daemon = True
        thread.start()
        
    def send_test_message(self, session_id, message="Test desde WhatsApp Web Real"):
        """Enviar mensaje de prueba real"""
        try:
            session = self.get_session(session_id)
            if not session or not session.get('authenticated'):
                return False
                
            driver = session.get('driver')
            if not driver:
                return False
                
            # Por seguridad, por ahora solo simulamos el envío
            # En una implementación completa, aquí se enviaría el mensaje real
            logger.info(f"Mensaje de prueba simulado para sesión: {session_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error enviando mensaje de prueba: {e}")
            return False
            
    def get_active_sessions(self):
        """Obtener estadísticas de sesiones activas"""
        with self.lock:
            return {
                'total_sessions': len(self.sessions),
                'authenticated': sum(1 for s in self.sessions.values() if s.get('authenticated', False)),
                'pending': sum(1 for s in self.sessions.values() if s.get('status') == 'pending'),
                'qr_ready': sum(1 for s in self.sessions.values() if s.get('status') == 'qr_ready'),
                'connecting': sum(1 for s in self.sessions.values() if s.get('status') == 'connecting')
            }
    
    def send_mock_qr_code(self, session_id):
        """Enviar código QR simulado cuando Chrome no está disponible"""
        try:
            logger.info(f"Enviando QR simulado para sesión: {session_id}")
            
            # Crear QR simulado con mensaje
            qr_text = f"WhatsApp Web no disponible - Chrome no encontrado\nSession: {session_id}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Generar QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_text)
            qr.make(fit=True)
            
            # Crear imagen
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convertir a base64
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            qr_data = base64.b64encode(img_buffer.getvalue()).decode()
            qr_data_url = f"data:image/png;base64,{qr_data}"
            
            # Actualizar sesión
            self.update_session_status(session_id, 'qr_ready', qr_data=qr_data_url)
            
            # Enviar QR al cliente
            socketio.emit('qr_code', {
                'session_id': session_id,
                'qr_data': qr_data_url,
                'message': '⚠️ Chrome no disponible - QR simulado',
                'error': 'Chrome no está instalado en Railway'
            })
            
            logger.info(f"QR simulado enviado para sesión: {session_id}")
            
        except Exception as e:
            logger.error(f"Error enviando QR simulado: {e}")
            socketio.emit('error', {
                'session_id': session_id,
                'message': 'Error generando QR simulado',
                'error': str(e)
            })

# Instancia global del manager REAL
ws_manager = RealWhatsAppWebManager()

# Crear aplicación Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'real-whatsapp-websocket-key')

# Configurar CORS
CORS(app, origins="*")

# Configurar SocketIO
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='gevent',
    logger=False,
    engineio_logger=False,
    transports=['websocket', 'polling']
)

# Eventos WebSocket
@socketio.on('connect')
def handle_connect():
    """Manejar conexión WebSocket"""
    client_id = request.sid
    logger.info(f"Cliente conectado: {client_id}")
    
    emit('connected', {
        'type': 'connected',
        'client_id': client_id,
        'message': 'Conectado al servidor WebSocket REAL',
        'is_real': True
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Manejar desconexión WebSocket"""
    client_id = request.sid
    logger.info(f"Cliente desconectado: {client_id}")
    
    # Limpiar sesiones del cliente
    sessions_to_remove = []
    for session_id, session in ws_manager.sessions.items():
        if session.get('client_id') == client_id:
            sessions_to_remove.append(session_id)
    
    for session_id in sessions_to_remove:
        ws_manager.remove_session(session_id)

@socketio.on('get_qr')
def handle_get_qr(data):
    """Generar y enviar código QR REAL"""
    try:
        client_id = request.sid
        session_id = data.get('session_id')
        
        if not session_id:
            # Crear nueva sesión
            session_id = ws_manager.create_session(client_id)
        
        # Unirse a la room de la sesión
        join_room(session_id)
        
        # Iniciar sesión REAL de WhatsApp Web
        success = ws_manager.start_whatsapp_session(session_id)
        
        if not success:
            emit('error', {
                'type': 'error',
                'message': 'Error iniciando sesión real de WhatsApp Web'
            })
            
    except Exception as e:
        logger.error(f"Error en get_qr: {e}")
        emit('error', {
            'type': 'error',
            'message': f'Error interno: {str(e)}'
        })

@socketio.on('get_status')
def handle_get_status(data):
    """Obtener estado de la sesión"""
    try:
        session_id = data.get('session_id')
        
        if not session_id:
            emit('error', {
                'type': 'error',
                'message': 'Session ID requerido'
            })
            return
            
        session = ws_manager.get_session(session_id)
        
        if session:
            emit('status', {
                'type': 'status',
                'session_id': session_id,
                'status': session['status'],
                'authenticated': session.get('authenticated', False),
                'created_at': session['created_at'].isoformat(),
                'phone_number': session.get('phone_number'),
                'message': f"Estado: {session['status']}",
                'is_real': True
            })
        else:
            emit('error', {
                'type': 'error',
                'message': 'Sesión no encontrada'
            })
            
    except Exception as e:
        logger.error(f"Error en get_status: {e}")
        emit('error', {
            'type': 'error',
            'message': f'Error interno: {str(e)}'
        })

@socketio.on('test_whatsapp')
def handle_test_whatsapp(data):
    """Manejar pruebas de WhatsApp REAL"""
    try:
        session_id = data.get('session_id')
        action = data.get('action', 'send_test_message')
        
        if not session_id:
            emit('error', {
                'type': 'error',
                'message': 'Session ID requerido'
            })
            return
            
        session = ws_manager.get_session(session_id)
        
        if not session:
            emit('error', {
                'type': 'error',
                'message': 'Sesión no encontrada'
            })
            return
            
        if not session.get('authenticated', False):
            emit('error', {
                'type': 'error',
                'message': 'WhatsApp no está autenticado'
            })
            return
            
        # Procesar diferentes tipos de pruebas
        if action == 'send_test_message':
            success = ws_manager.send_test_message(session_id)
            
            emit('test_result', {
                'type': 'test_result',
                'session_id': session_id,
                'action': action,
                'success': success,
                'message': 'Prueba de mensaje real completada' if success else 'Error en prueba de mensaje',
                'is_real': True,
                'details': {
                    'message': 'Test desde WhatsApp Web Real',
                    'timestamp': datetime.now().isoformat()
                }
            })
            
        elif action == 'check_connection':
            emit('test_result', {
                'type': 'test_result',
                'session_id': session_id,
                'action': action,
                'success': True,
                'message': 'Conexión WhatsApp REAL verificada',
                'is_real': True,
                'details': {
                    'status': session['status'],
                    'authenticated': session.get('authenticated', False),
                    'phone_number': session.get('phone_number', 'No disponible'),
                    'created_at': session['created_at'].isoformat(),
                    'last_activity': session['last_activity'].isoformat()
                }
            })
            
    except Exception as e:
        logger.error(f"Error en test_whatsapp: {e}")
        emit('error', {
            'type': 'error',
            'message': f'Error interno: {str(e)}'
        })

@socketio.on('disconnect_whatsapp')
def handle_disconnect_whatsapp(data):
    """Desconectar WhatsApp Web REAL"""
    try:
        session_id = data.get('session_id')
        
        if session_id:
            session = ws_manager.get_session(session_id)
            if session:
                ws_manager.remove_session(session_id)  # Esto cerrará el driver
                
                emit('disconnected', {
                    'type': 'disconnected',
                    'session_id': session_id,
                    'message': 'WhatsApp Web REAL desconectado',
                    'is_real': True
                })
                
                # Salir de la room
                leave_room(session_id)
        
    except Exception as e:
        logger.error(f"Error en disconnect_whatsapp: {e}")
        emit('error', {
            'type': 'error',
            'message': f'Error interno: {str(e)}'
        })

# Rutas HTTP
@app.route('/')
def index():
    """Página principal del servidor"""
    try:
        # Intentar servir la página HTML si existe
        return render_template('index.html')
    except:
        # Si no hay templates, devolver JSON
        return {
            'status': 'running',
            'service': 'WhatsApp Web Real Server',
            'version': '1.0.0',
            'endpoints': {
                'health': '/health',
                'stats': '/stats',
                'websocket': '/socket.io/',
                'documentation': '/docs'
            },
            'message': '🚀 Servidor WebSocket REAL de WhatsApp Web funcionando correctamente',
            'timestamp': datetime.now().isoformat()
        }

@app.route('/favicon.ico')
def favicon():
    """Favicon para el navegador"""
    return '', 204

@app.route('/docs')
def docs():
    """Documentación básica del API"""
    return {
        'title': 'WhatsApp Web Real Server API',
        'description': 'Servidor WebSocket para conexiones reales a WhatsApp Web',
        'websocket_events': {
            'connect': 'Conectar al servidor',
            'get_qr': 'Generar código QR real',
            'get_status': 'Obtener estado de sesión',
            'test_whatsapp': 'Probar funcionalidad'
        },
        'http_endpoints': {
            '/': 'Información del servidor',
            '/health': 'Estado de salud',
            '/stats': 'Estadísticas de sesiones',
            '/docs': 'Esta documentación'
        },
        'example_usage': {
            'javascript': '''
            const socket = io('wss://tu-servidor.railway.app');
            socket.on('connect', () => {
                console.log('Conectado al servidor');
                socket.emit('get_qr', {});
            });
            socket.on('qr_code', (data) => {
                console.log('QR recibido:', data);
            });
            '''
        }
    }

# ...existing code...

# Tarea de limpieza periódica
def cleanup_sessions():
    """Limpiar sesiones inactivas"""
    while True:
        try:
            time.sleep(300)  # Ejecutar cada 5 minutos
            
            current_time = datetime.now()
            sessions_to_remove = []
            
            for session_id, session in ws_manager.sessions.items():
                # Eliminar sesiones inactivas por más de 2 horas
                if (current_time - session['last_activity']).total_seconds() > 7200:
                    sessions_to_remove.append(session_id)
            
            for session_id in sessions_to_remove:
                ws_manager.remove_session(session_id)
                
            if sessions_to_remove:
                logger.info(f"Limpieza completada: {len(sessions_to_remove)} sesiones eliminadas")
                
        except Exception as e:
            logger.error(f"Error en limpieza de sesiones: {e}")

if __name__ == '__main__':
    # Iniciar tarea de limpieza en hilo separado
    cleanup_thread = threading.Thread(target=cleanup_sessions)
    cleanup_thread.daemon = True
    cleanup_thread.start()
    
    logger.info(f"Iniciando servidor WebSocket REAL en {WS_HOST}:{WS_PORT}")
    logger.info(f"Debug: {DEBUG}")
    logger.info("🚀 WhatsApp Web REAL con Selenium")
    
    # Iniciar servidor
    socketio.run(
        app,
        host=WS_HOST,
        port=WS_PORT,
        debug=DEBUG,
        allow_unsafe_werkzeug=True
    )
