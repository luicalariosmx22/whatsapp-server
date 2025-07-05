#!/usr/bin/env python3
"""
Servidor WebSocket independiente para WhatsApp Web
Este servidor maneja las conexiones WebSocket para el módulo QR WhatsApp Web
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

class WhatsAppWebSocketManager:
    """Gestor de sesiones WebSocket para WhatsApp Web"""
    
    def __init__(self):
        self.sessions = {}
        self.active_connections = {}
        self.whatsapp_clients = {}
        self.lock = threading.Lock()
        
    def create_session(self, client_id):
        """Crear nueva sesión de WhatsApp Web"""
        with self.lock:
            session_id = str(uuid.uuid4())
            self.sessions[session_id] = {
                'client_id': client_id,
                'status': 'pending',
                'created_at': datetime.now(),
                'qr_code': None,
                'authenticated': False,
                'last_activity': datetime.now()
            }
            logger.info(f"Sesión creada: {session_id} para cliente {client_id}")
            return session_id
        
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
        """Eliminar sesión"""
        with self.lock:
            if session_id in self.sessions:
                del self.sessions[session_id]
                logger.info(f"Sesión eliminada: {session_id}")
                
    def generate_qr_code(self, session_id):
        """Generar código QR para WhatsApp Web"""
        try:
            # En una implementación real, aquí se conectaría con una librería 
            # como whatsapp-web.js, go-whatsapp, baileys, etc.
            # Por ahora, generamos datos simulados para demostración
            
            timestamp = int(time.time())
            qr_data = f"1@{session_id},{timestamp},whatsapp-web-demo"
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convertir a base64
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
            
            # Actualizar sesión
            self.update_session_status(session_id, 'qr_ready', qr_code=img_base64)
            
            # Simular autenticación automática después de 15 segundos
            self.simulate_authentication(session_id)
            
            return qr_data
            
        except Exception as e:
            logger.error(f"Error generando QR: {e}")
            return None
            
    def simulate_authentication(self, session_id):
        """Simular autenticación de WhatsApp Web (para demostración)"""
        def authenticate_after_delay():
            try:
                # Simular tiempo de escaneo y autenticación
                time.sleep(15)
                
                session = self.get_session(session_id)
                if session and session['status'] == 'qr_ready':
                    # Actualizar estado a autenticado
                    self.update_session_status(session_id, 'authenticated', authenticated=True)
                    
                    # Emitir evento de autenticación
                    socketio.emit('authenticated', {
                        'type': 'authenticated',
                        'session_id': session_id,
                        'message': '¡Autenticación exitosa!',
                        'timestamp': datetime.now().isoformat()
                    }, room=session_id)
                    
                    logger.info(f"Autenticación simulada exitosa para sesión: {session_id}")
                    
                    # Mantener sesión viva con heartbeat
                    self.start_session_heartbeat(session_id)
                    
            except Exception as e:
                logger.error(f"Error en simulación de autenticación: {e}")
                
        # Ejecutar en hilo separado
        thread = threading.Thread(target=authenticate_after_delay)
        thread.daemon = True
        thread.start()
        
    def start_session_heartbeat(self, session_id):
        """Iniciar heartbeat para mantener sesión viva"""
        def heartbeat():
            while True:
                try:
                    session = self.get_session(session_id)
                    if not session or session.get('status') != 'authenticated':
                        break
                        
                    # Actualizar última actividad
                    self.update_session_status(session_id, 'authenticated')
                    
                    # Emitir heartbeat cada 30 segundos
                    socketio.emit('heartbeat', {
                        'type': 'heartbeat',
                        'session_id': session_id,
                        'timestamp': datetime.now().isoformat()
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
                'qr_ready': sum(1 for s in self.sessions.values() if s.get('status') == 'qr_ready')
            }

# Instancia global del manager
ws_manager = WhatsAppWebSocketManager()

# Crear aplicación Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'whatsapp-websocket-secret-key')

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
        'message': 'Conectado al servidor WebSocket'
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
    """Generar y enviar código QR"""
    try:
        client_id = request.sid
        session_id = data.get('session_id')
        
        if not session_id:
            # Crear nueva sesión
            session_id = ws_manager.create_session(client_id)
        
        # Unirse a la room de la sesión
        join_room(session_id)
        
        # Generar QR
        qr_data = ws_manager.generate_qr_code(session_id)
        
        if qr_data:
            emit('qr_code', {
                'type': 'qr_code',
                'session_id': session_id,
                'qr_data': qr_data,
                'message': 'Código QR generado'
            })
        else:
            emit('error', {
                'type': 'error',
                'message': 'Error al generar código QR'
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
                'message': f"Estado: {session['status']}"
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
    """Manejar pruebas de WhatsApp"""
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
            # Simular envío de mensaje de prueba
            def send_test_message():
                time.sleep(2)  # Simular tiempo de envío
                
                emit('test_result', {
                    'type': 'test_result',
                    'session_id': session_id,
                    'action': action,
                    'success': True,
                    'message': 'Mensaje de prueba enviado exitosamente',
                    'details': {
                        'to': 'Número de prueba',
                        'message': 'Hola! Este es un mensaje de prueba desde WhatsApp Web.',
                        'timestamp': datetime.now().isoformat()
                    }
                })
                
            thread = threading.Thread(target=send_test_message)
            thread.daemon = True
            thread.start()
            
        elif action == 'check_connection':
            # Verificar estado de conexión
            emit('test_result', {
                'type': 'test_result',
                'session_id': session_id,
                'action': action,
                'success': True,
                'message': 'Conexión WhatsApp verificada',
                'details': {
                    'status': session['status'],
                    'authenticated': session.get('authenticated', False),
                    'created_at': session['created_at'].isoformat(),
                    'last_activity': session['last_activity'].isoformat()
                }
            })
            
        else:
            emit('error', {
                'type': 'error',
                'message': f'Acción no reconocida: {action}'
            })
            
    except Exception as e:
        logger.error(f"Error en test_whatsapp: {e}")
        emit('error', {
            'type': 'error',
            'message': f'Error interno: {str(e)}'
        })

@socketio.on('disconnect_whatsapp')
def handle_disconnect_whatsapp(data):
    """Desconectar WhatsApp Web"""
    try:
        session_id = data.get('session_id')
        
        if session_id:
            session = ws_manager.get_session(session_id)
            if session:
                ws_manager.update_session_status(session_id, 'disconnected', authenticated=False)
                
                emit('disconnected', {
                    'type': 'disconnected',
                    'session_id': session_id,
                    'message': 'WhatsApp Web desconectado'
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
@app.route('/health')
def health_check():
    """Verificación de salud del servidor"""
    stats = ws_manager.get_active_sessions()
    return {
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'sessions': stats
    }

@app.route('/stats')
def get_stats():
    """Obtener estadísticas del servidor"""
    stats = ws_manager.get_active_sessions()
    return {
        'active_sessions': stats,
        'server_info': {
            'host': WS_HOST,
            'port': WS_PORT,
            'debug': DEBUG
        }
    }

# Tarea de limpieza periódica
def cleanup_sessions():
    """Limpiar sesiones inactivas"""
    while True:
        try:
            time.sleep(300)  # Ejecutar cada 5 minutos
            
            current_time = datetime.now()
            sessions_to_remove = []
            
            for session_id, session in ws_manager.sessions.items():
                # Eliminar sesiones inactivas por más de 1 hora
                if (current_time - session['last_activity']).total_seconds() > 3600:
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
    
    logger.info(f"Iniciando servidor WebSocket en {WS_HOST}:{WS_PORT}")
    logger.info(f"Debug: {DEBUG}")
    
    # Iniciar servidor
    socketio.run(
        app,
        host=WS_HOST,
        port=WS_PORT,
        debug=DEBUG,
        allow_unsafe_werkzeug=True
    )
