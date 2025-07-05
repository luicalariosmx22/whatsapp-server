#!/usr/bin/env python3
"""
Script para iniciar el servidor WebSocket de WhatsApp Web
"""

import os
import sys
import signal
import threading
import time
from datetime import datetime

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from websocket_server import socketio, app, logger, WS_HOST, WS_PORT

def signal_handler(signum, frame):
    """Manejar señales para cierre limpio"""
    logger.info("🛑 Señal de cierre recibida, cerrando servidor...")
    sys.exit(0)

def check_dependencies():
    """Verificar dependencias necesarias"""
    required_packages = [
        'flask',
        'flask-socketio',
        'flask-cors',
        'qrcode',
        'python-socketio'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Dependencias faltantes: {', '.join(missing)}")
        print("📦 Instala con: pip install " + ' '.join(missing))
        return False
    
    return True

def start_server():
    """Iniciar el servidor WebSocket"""
    
    print("🚀 Iniciando servidor WebSocket de WhatsApp Web")
    print("=" * 60)
    print(f"🌐 Host: {WS_HOST}")
    print(f"🔌 Puerto: {WS_PORT}")
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Verificar dependencias
    if not check_dependencies():
        return
    
    # Configurar manejadores de señales
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Mensaje de inicio
    logger.info("🎯 Servidor WebSocket iniciado correctamente")
    logger.info("📱 Listo para recibir conexiones de WhatsApp Web")
    logger.info("🔗 Endpoints disponibles:")
    logger.info("   - WebSocket: ws://{WS_HOST}:{WS_PORT}/socket.io/")
    logger.info("   - Health: http://{WS_HOST}:{WS_PORT}/health")
    logger.info("   - Stats: http://{WS_HOST}:{WS_PORT}/stats")
    
    try:
        # Iniciar servidor
        socketio.run(
            app,
            host=WS_HOST,
            port=WS_PORT,
            debug=False,
            allow_unsafe_werkzeug=True,
            use_reloader=False
        )
    except Exception as e:
        logger.error(f"❌ Error al iniciar servidor: {e}")
        print(f"❌ Error al iniciar servidor: {e}")

if __name__ == '__main__':
    start_server()
