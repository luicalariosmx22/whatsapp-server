from flask import Flask
from flask_socketio import SocketIO, emit, disconnect, join_room, leave_room
import json
import uuid
import time
import threading
import qrcode
import io
import base64
from datetime import datetime
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WhatsAppWebSocketManager:
    def __init__(self):
        self.sessions = {}
        self.active_connections = {}
        self.whatsapp_clients = {}
        
    def create_session(self, client_id):
        """Crear nueva sesión de WhatsApp Web"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            'client_id': client_id,
            'status': 'pending',
            'created_at': datetime.now(),
            'qr_code': None,
            'authenticated': False
        }
        return session_id
        
    def get_session(self, session_id):
        """Obtener sesión por ID"""
        return self.sessions.get(session_id)
        
    def update_session_status(self, session_id, status, **kwargs):
        """Actualizar estado de sesión"""
        if session_id in self.sessions:
            self.sessions[session_id]['status'] = status
            self.sessions[session_id].update(kwargs)
            
    def generate_qr_code(self, session_id):
        """Generar código QR para WhatsApp Web"""
        try:
            # En una implementación real, aquí se generaría el QR real de WhatsApp Web
            # Por ahora, generamos un QR con datos simulados
            qr_data = f"whatsapp-web-session:{session_id}:{int(time.time())}"
            
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
            
            return qr_data
            
        except Exception as e:
            logger.error(f"Error generando QR: {e}")
            return None
            
    def simulate_whatsapp_connection(self, session_id):
        """Simular conexión de WhatsApp Web (para demostración)"""
        def connect_after_delay():
            time.sleep(10)  # Simular tiempo de escaneo
            
            if session_id in self.sessions:
                self.update_session_status(session_id, 'authenticated', authenticated=True)
                
                # Enviar evento a todos los clientes de esta sesión
                from flask_socketio import emit
                emit('whatsapp_authenticated', {
                    'session_id': session_id,
                    'status': 'connected',
                    'message': 'WhatsApp Web conectado exitosamente'
                }, room=session_id)
                
        # Ejecutar en hilo separado
        thread = threading.Thread(target=connect_after_delay)
        thread.daemon = True
        thread.start()

# Instancia global del manager
ws_manager = WhatsAppWebSocketManager()

def init_websocket(app):
    """Inicializar WebSocket con Flask-SocketIO"""
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    
    @socketio.on('connect', namespace='/ws/whatsapp')
    def handle_connect():
        logger.info(f"Cliente conectado: {request.sid}")
        emit('connected', {'message': 'Conectado al servidor WebSocket'})
        
    @socketio.on('disconnect', namespace='/ws/whatsapp')
    def handle_disconnect():
        logger.info(f"Cliente desconectado: {request.sid}")
        
        # Limpiar sesiones del cliente
        client_sessions = [sid for sid, session in ws_manager.sessions.items() 
                          if session.get('client_id') == request.sid]
        
        for session_id in client_sessions:
            if session_id in ws_manager.sessions:
                del ws_manager.sessions[session_id]
                
    @socketio.on('get_qr', namespace='/ws/whatsapp')
    def handle_get_qr(data):
        """Generar y enviar código QR"""
        try:
            session_id = data.get('session_id')
            
            if not session_id:
                # Crear nueva sesión
                session_id = ws_manager.create_session(request.sid)
                
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
                
                # Simular conexión automática (para demostración)
                ws_manager.simulate_whatsapp_connection(session_id)
                
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
            
    @socketio.on('get_status', namespace='/ws/whatsapp')
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
            
    @socketio.on('disconnect_whatsapp', namespace='/ws/whatsapp')
    def handle_disconnect_whatsapp(data):
        """Desconectar WhatsApp Web"""
        try:
            session_id = data.get('session_id')
            
            if session_id and session_id in ws_manager.sessions:
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
    
    return socketio

# Función para uso con Flask-SocketIO independiente
def create_websocket_app():
    """Crear aplicación Flask-SocketIO independiente"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'whatsapp-websocket-secret'
    
    socketio = init_websocket(app)
    
    @app.route('/health')
    def health_check():
        return {'status': 'ok', 'active_sessions': len(ws_manager.sessions)}
        
    return app, socketio

if __name__ == '__main__':
    # Ejecutar servidor WebSocket independiente
    app, socketio = create_websocket_app()
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)
