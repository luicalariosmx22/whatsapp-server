#!/usr/bin/env python3
"""
Script para iniciar el servidor WebSocket REAL de WhatsApp Web
"""

import os
import sys
import signal
import subprocess

def check_chrome():
    """Verificar que Chrome esté instalado"""
    try:
        result = subprocess.run(['google-chrome', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Google Chrome encontrado: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    try:
        result = subprocess.run(['chromium-browser', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Chromium encontrado: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ Chrome/Chromium no encontrado")
    print("📦 Instala Chrome con:")
    print("   Ubuntu/Debian: sudo apt install google-chrome-stable")
    print("   WSL: Instala Chrome en Windows")
    return False

def start_real_server():
    """Iniciar el servidor WebSocket REAL"""
    print("🚀 Iniciando servidor WebSocket REAL de WhatsApp Web")
    print("=" * 60)
    
    # Verificar Chrome
    if not check_chrome():
        return
    
    # Variables de entorno
    os.environ['WS_PORT'] = '5001'
    os.environ['WS_HOST'] = '0.0.0.0'
    os.environ['HEADLESS'] = 'False'  # Para ver el navegador
    
    print("🌐 Configuración:")
    print(f"   Puerto: {os.environ['WS_PORT']}")
    print(f"   Host: {os.environ['WS_HOST']}")
    print(f"   Headless: {os.environ['HEADLESS']}")
    print("=" * 60)
    
    try:
        # Iniciar servidor
        from real_websocket_server import socketio, app, logger
        
        logger.info("🎯 Servidor WebSocket REAL iniciado")
        logger.info("📱 Conectando con WhatsApp Web usando Selenium")
        logger.info("🔗 Endpoints disponibles:")
        logger.info(f"   - WebSocket: ws://localhost:5001/socket.io/")
        logger.info(f"   - Health: http://localhost:5001/health")
        logger.info(f"   - Stats: http://localhost:5001/stats")
        
        socketio.run(
            app,
            host='0.0.0.0',
            port=5001,
            debug=False,
            allow_unsafe_werkzeug=True
        )
        
    except Exception as e:
        print(f"❌ Error iniciando servidor: {e}")

if __name__ == '__main__':
    start_real_server()
