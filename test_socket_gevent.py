#!/usr/bin/env python3
"""
Servidor de prueba Socket.IO usando gevent
"""
from flask import Flask
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu-clave-secreta'
CORS(app)

# Usar gevent en lugar de eventlet
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='gevent',
    logger=True,
    engineio_logger=True
)

@app.route('/')
def index():
    return "Servidor Socket.IO funcionando"

@app.route('/health')
def health():
    return {"status": "ok", "async_mode": socketio.async_mode}

@socketio.on('connect')
def handle_connect():
    logger.info(f"Cliente conectado")
    emit('status', {'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f"Cliente desconectado")

@socketio.on('message')
def handle_message(data):
    logger.info(f"Mensaje recibido: {data}")
    emit('response', {'message': 'Mensaje recibido'})

if __name__ == '__main__':
    logger.info("Iniciando servidor Socket.IO con gevent")
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)
