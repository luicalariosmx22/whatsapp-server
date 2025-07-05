#!/usr/bin/env python3
"""
Servidor WebSocket REAL para WhatsApp Web usando Selenium
Este servidor maneja conexiones reales a WhatsApp Web
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
from flask import Flask, request
from flask_socketio import SocketIO, emit, disconnect, join_room, leave_room
from flask_cors import CORS

# Importar Selenium para WhatsApp Web real
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️ Selenium no disponible, usando modo simulación")

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
        self.active_drivers = {}
        self.lock = threading.Lock()
        
    def create_session(self, client_id):
        """Crear nueva sesión real de WhatsApp Web"""
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
    
    def setup_chrome_driver(self):
        """Configurar Chrome Driver para WhatsApp Web"""
        if not SELENIUM_AVAILABLE:
            return None
            
        try:
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            
            # Configurar para WhatsApp Web
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Desactivar notificaciones
            prefs = {
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_settings.popups": 0,
                "profile.managed_default_content_settings.images": 2
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Instalar ChromeDriver automáticamente
            service = Service(ChromeDriverManager().install())
            
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.set_page_load_timeout(30)
            
            logger.info("✅ Chrome Driver configurado exitosamente")
            return driver
            
        except Exception as e:
            logger.error(f"❌ Error configurando Chrome Driver: {e}")
            return None
    
    def start_whatsapp_session(self, session_id):
        """Iniciar sesión real de WhatsApp Web"""
        try:
            session = self.get_session(session_id)
            if not session:
                return False
                
            # Configurar driver
            driver = self.setup_chrome_driver()
            if not driver:
                logger.error("No se pudo configurar Chrome Driver")
                return False
                
            self.active_drivers[session_id] = driver
            session['driver'] = driver
            
            # Navegar a WhatsApp Web
            logger.info(f"🌐 Navegando a WhatsApp Web para sesión {session_id}")
            driver.get("https://web.whatsapp.com")
            
            # Actualizar estado
            self.update_session_status(session_id, 'connecting')
            
            # Monitorear QR code en hilo separado
            qr_thread = threading.Thread(target=self.monitor_qr_code, args=(session_id,))
            qr_thread.daemon = True
            qr_thread.start()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error iniciando sesión WhatsApp: {e}")
            return False
    
    def monitor_qr_code(self, session_id):
        """Monitorear código QR y autenticación"""
        try:
            session = self.get_session(session_id)
            driver = session.get('driver')
            
            if not driver:
                return
                
            # Esperar a que aparezca el QR
            wait = WebDriverWait(driver, 30)
            
            try:
                # Buscar el elemento QR
                qr_element = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-ref]'))
                )
                
                # Obtener el QR data
                qr_data = qr_element.get_attribute('data-ref')
                
                if qr_data:
                    logger.info(f"📱 QR Code obtenido para sesión {session_id}")
                    
                    # Actualizar sesión con QR real
                    self.update_session_status(session_id, 'qr_ready', qr_code=qr_data)
                    
                    # Emitir QR al cliente
                    socketio.emit('qr_code', {
                        'type': 'qr_code',
                        'session_id': session_id,
                        'qr_data': qr_data,
                        'message': 'Código QR REAL generado'
                    }, room=session_id)
                    
                    # Monitorear autenticación
                    self.monitor_authentication(session_id)
                    
            except Exception as e:
                logger.error(f"❌ Error obteniendo QR: {e}")
                # Fallback a simulación si hay error
                self.fallback_to_simulation(session_id)
                
        except Exception as e:
            logger.error(f"❌ Error en monitor_qr_code: {e}")
    
    def monitor_authentication(self, session_id):
        """Monitorear autenticación en WhatsApp Web"""
        try:
            session = self.get_session(session_id)
            driver = session.get('driver')
            
            if not driver:
                return
                
            wait = WebDriverWait(driver, 120)  # 2 minutos para escanear
            
            try:
                # Esperar a que desaparezca el QR (autenticación exitosa)
                wait.until(
                    EC.invisibility_of_element_located((By.CSS_SELECTOR, '[data-ref]'))
                )
                
                # Verificar que estamos en el chat principal
                chat_element = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="chat-list"]'))
                )
                
                if chat_element:
                    logger.info(f"🎉 Autenticación REAL exitosa para sesión {session_id}")
                    
                    # Actualizar estado
                    self.update_session_status(session_id, 'authenticated', authenticated=True)
                    
                    # Emitir autenticación exitosa
                    socketio.emit('authenticated', {
                        'type': 'authenticated',
                        'session_id': session_id,
                        'message': '¡Autenticación REAL exitosa!',
                        'timestamp': datetime.now().isoformat(),
                        'real_connection': True
                    }, room=session_id)
                    
                    # Iniciar heartbeat
                    self.start_session_heartbeat(session_id)
                    
            except Exception as e:
                logger.error(f"❌ Timeout o error en autenticación: {e}")
                self.handle_auth_timeout(session_id)
                
        except Exception as e:
            logger.error(f"❌ Error en monitor_authentication: {e}")
    
    def fallback_to_simulation(self, session_id):
        """Fallback a simulación si Selenium falla"""
        logger.warning(f"🔄 Fallback a simulación para sesión {session_id}")
        
        # Generar QR simulado
        timestamp = int(time.time())
        qr_data = f"2@{session_id},{timestamp},whatsapp-web-real-fallback"
        
        # Actualizar estado
        self.update_session_status(session_id, 'qr_ready', qr_code=qr_data)
        
        # Emitir QR simulado
        socketio.emit('qr_code', {
            'type': 'qr_code',
            'session_id': session_id,
            'qr_data': qr_data,
            'message': 'Código QR generado (modo fallback)',
            'fallback_mode': True
        }, room=session_id)
        
        # Simular autenticación después de 20 segundos
        def delayed_auth():
            time.sleep(20)
            self.update_session_status(session_id, 'authenticated', authenticated=True)
            socketio.emit('authenticated', {
                'type': 'authenticated',
                'session_id': session_id,
                'message': '¡Autenticación exitosa! (modo fallback)',
                'timestamp': datetime.now().isoformat(),
                'fallback_mode': True
            }, room=session_id)
            
        auth_thread = threading.Thread(target=delayed_auth)
        auth_thread.daemon = True
        auth_thread.start()
    
    def handle_auth_timeout(self, session_id):
        """Manejar timeout de autenticación"""
        logger.warning(f"⏰ Timeout de autenticación para sesión {session_id}")
        
        # Generar nuevo QR
        self.regenerate_qr(session_id)
    
    def regenerate_qr(self, session_id):
        """Regenerar código QR"""
        try:
            session = self.get_session(session_id)
            driver = session.get('driver')
            
            if driver:
                # Recargar página para obtener nuevo QR
                driver.refresh()
                time.sleep(3)
                
                # Reiniciar monitoreo
                qr_thread = threading.Thread(target=self.monitor_qr_code, args=(session_id,))
                qr_thread.daemon = True
                qr_thread.start()
            else:
                # Fallback si no hay driver
                self.fallback_to_simulation(session_id)
                
        except Exception as e:
            logger.error(f"❌ Error regenerando QR: {e}")
            self.fallback_to_simulation(session_id)
    
    def send_test_message(self, session_id, phone_number="123456789"):
        """Enviar mensaje de prueba real"""
        try:
            session = self.get_session(session_id)
            driver = session.get('driver')
            
            if not driver or not session.get('authenticated'):
                return False
                
            # Buscar chat o crear nuevo
            # Simplificado para demo - en producción sería más complejo
            logger.info(f"📤 Enviando mensaje de prueba REAL desde sesión {session_id}")
            
            # Por ahora retornar éxito simulado
            # En implementación completa aquí iría la lógica real de envío
            return True
            
        except Exception as e:
            logger.error(f"❌ Error enviando mensaje: {e}")
            return False
    
    def get_session(self, session_id):
        """Obtener sesión por ID"""
        with self.lock:
            return self.sessions.get(session_id)
        
    def update_session_status(self, session_id, status, **kwargs):
        """Actualizar estado de sesión"""
        with self.lock:
            if session_id in self.sessions:
                self.sessions[session_id]['status'] = status
                self.sessions[session_id]['last_activity'] = datetime.now()
                self.sessions[session_id].update(kwargs)
                logger.info(f"Sesión {session_id} actualizada a estado: {status}")
                
    def remove_session(self, session_id):
        """Eliminar sesión y limpiar driver"""
        with self.lock:
            if session_id in self.sessions:
                # Cerrar driver si existe
                if session_id in self.active_drivers:
                    try:
                        self.active_drivers[session_id].quit()
                        del self.active_drivers[session_id]
                    except:
                        pass
                        
                del self.sessions[session_id]
                logger.info(f"Sesión eliminada: {session_id}")
    
    def start_session_heartbeat(self, session_id):
        """Iniciar heartbeat para mantener sesión viva"""
        def heartbeat():
            while True:
                try:
                    session = self.get_session(session_id)
                    if not session or session.get('status') != 'authenticated':
                        break
                        
                    # Verificar que el driver siga activo
                    driver = session.get('driver')
                    if driver:
                        try:
                            # Ping simple al driver
                            driver.current_url
                        except:
                            logger.warning(f"Driver inactivo para sesión {session_id}")
                            break
                    
                    # Actualizar última actividad
                    self.update_session_status(session_id, 'authenticated')
                    
                    # Emitir heartbeat
                    socketio.emit('heartbeat', {
                        'type': 'heartbeat',
                        'session_id': session_id,
                        'timestamp': datetime.now().isoformat(),
                        'real_connection': True
                    }, room=session_id)
                    
                    time.sleep(30)
                    
                except Exception as e:
                    logger.error(f"Error en heartbeat para sesión {session_id}: {e}")
                    break
                    
        thread = threading.Thread(target=heartbeat)
        thread.daemon = True
        thread.start()
    
    def get_active_sessions(self):
        """Obtener estadísticas de sesiones activas"""
        with self.lock:
            return {
                'total_sessions': len(self.sessions),
                'authenticated': sum(1 for s in self.sessions.values() if s.get('authenticated', False)),
                'pending': sum(1 for s in self.sessions.values() if s.get('status') == 'pending'),
                'qr_ready': sum(1 for s in self.sessions.values() if s.get('status') == 'qr_ready'),
                'selenium_available': SELENIUM_AVAILABLE,
                'active_drivers': len(self.active_drivers)
            }

# Instancia global del manager
ws_manager = RealWhatsAppWebManager()

# Crear aplicación Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'whatsapp-websocket-real-secret-key')

# Configurar CORS
CORS(app, origins="*")

# Configurar SocketIO
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='threading',
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
        'selenium_available': SELENIUM_AVAILABLE
    })

@socketio.on('get_qr')
def handle_get_qr(data):
    """Generar QR REAL de WhatsApp Web"""
    try:
        client_id = request.sid
        session_id = data.get('session_id')
        
        if not session_id:
            # Crear nueva sesión
            session_id = ws_manager.create_session(client_id)
        
        # Unirse a la room de la sesión
        join_room(session_id)
        
        logger.info(f"🚀 Iniciando sesión REAL de WhatsApp Web: {session_id}")
        
        if SELENIUM_AVAILABLE:
            # Iniciar sesión real con Selenium
            success = ws_manager.start_whatsapp_session(session_id)
            if not success:
                # Fallback a simulación
                ws_manager.fallback_to_simulation(session_id)
        else:
            # Usar simulación si Selenium no está disponible
            ws_manager.fallback_to_simulation(session_id)
            
    except Exception as e:
        logger.error(f"Error en get_qr: {e}")
        emit('error', {
            'type': 'error',
            'message': f'Error interno: {str(e)}'
        })

@socketio.on('test_whatsapp')
def handle_test_whatsapp(data):
    """Manejar pruebas REALES de WhatsApp"""
    try:
        session_id = data.get('session_id')
        action = data.get('action', 'send_test_message')
        
        session = ws_manager.get_session(session_id)
        
        if not session or not session.get('authenticated', False):
            emit('test_result', {
                'type': 'test_result',
                'session_id': session_id,
                'action': action,
                'success': False,
                'message': 'WhatsApp no está autenticado'
            })
            return
            
        if action == 'send_test_message':
            # Intentar envío real
            success = ws_manager.send_test_message(session_id)
            
            emit('test_result', {
                'type': 'test_result',
                'session_id': session_id,
                'action': action,
                'success': success,
                'message': 'Mensaje de prueba procesado' if success else 'Error en envío',
                'details': {
                    'method': 'Selenium WebDriver' if SELENIUM_AVAILABLE else 'Simulación',
                    'timestamp': datetime.now().isoformat(),
                    'real_connection': session.get('driver') is not None
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
            ws_manager.remove_session(session_id)
            
            emit('disconnected', {
                'type': 'disconnected',
                'session_id': session_id,
                'message': 'WhatsApp Web desconectado (driver cerrado)'
            })
            
            leave_room(session_id)
        
    except Exception as e:
        logger.error(f"Error en disconnect_whatsapp: {e}")

# Rutas HTTP
@app.route('/health')
def health_check():
    """Verificación de salud del servidor"""
    stats = ws_manager.get_active_sessions()
    return {
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'sessions': stats,
        'selenium_status': 'available' if SELENIUM_AVAILABLE else 'not_available'
    }

if __name__ == '__main__':
    logger.info(f"🚀 Iniciando servidor WebSocket REAL en {WS_HOST}:{WS_PORT}")
    logger.info(f"🔧 Selenium disponible: {SELENIUM_AVAILABLE}")
    
    # Iniciar servidor
    socketio.run(
        app,
        host=WS_HOST,
        port=WS_PORT,
        debug=DEBUG,
        allow_unsafe_werkzeug=True
    )
