#!/usr/bin/env python3
"""
Servidor WebSocket simple para pruebas
"""
import os
from flask import Flask
from flask_socketio import SocketIO, emit
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-secret-key'
CORS(app, origins="*")

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    ping_timeout=120,
    ping_interval=25,
    logger=True,
    engineio_logger=True
)

@app.route('/health')
def health_check():
    return {'status': 'ok', 'message': 'Servidor funcionando'}

@socketio.on('connect')
def handle_connect():
    print(f"Cliente conectado: {request.sid}")
    emit('connected', {'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Cliente desconectado: {request.sid}")

@socketio.on('test_message')
def handle_test_message(data):
    print(f"Mensaje recibido: {data}")
    emit('test_response', {'received': data})

if __name__ == '__main__':
    print("🧪 Iniciando servidor de prueba...")
    socketio.run(
        app,
        host='0.0.0.0',
        port=5001,
        debug=True
    )
