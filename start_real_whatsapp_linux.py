#!/usr/bin/env python3
"""
Script para iniciar el servidor WebSocket REAL de WhatsApp Web en Linux/WSL
"""

import os
import sys
import signal
import subprocess

def check_chrome():
    """Verificar que Chrome/Chromium esté instalado"""
    # Verificar Google Chrome
    try:
        result = subprocess.run(['google-chrome', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Google Chrome encontrado: {result.stdout.strip()}")
            return 'google-chrome'
    except FileNotFoundError:
        pass
    
    # Verificar Chromium
    try:
        result = subprocess.run(['chromium-browser', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Chromium encontrado: {result.stdout.strip()}")
            return 'chromium-browser'
    except FileNotFoundError:
        pass
    
    # Verificar chromium (sin -browser)
    try:
        result = subprocess.run(['chromium', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Chromium encontrado: {result.stdout.strip()}")
            return 'chromium'
    except FileNotFoundError:
        pass
    
    print("❌ Chrome/Chromium no encontrado")
    print("📦 Instala con:")
    print("   Ubuntu/Debian: sudo apt install chromium-browser")
    print("   WSL: sudo apt install chromium-browser")
    return None

def check_packages():
    """Verificar paquetes de Python necesarios"""
    required_packages = [
        'flask',
        'flask_socketio',
        'flask_cors',
        'selenium',
        'webdriver_manager',
        'pillow',
        'qrcode'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing.append(package)
            print(f"❌ {package} - FALTA")
    
    if missing:
        print("\n📦 Instala los paquetes faltantes:")
        print(f"   pip install {' '.join(missing)}")
        return False
    
    return True

def start_real_server():
    """Iniciar el servidor WebSocket REAL"""
    print("🚀 Iniciando servidor WebSocket REAL de WhatsApp Web")
    print("=" * 60)
    
    # Verificar Chrome
    chrome_path = check_chrome()
    if not chrome_path:
        return
    
    # Verificar paquetes
    print("\n📦 Verificando paquetes de Python...")
    if not check_packages():
        return
    
    # Variables de entorno para WSL/Linux
    os.environ['WS_PORT'] = '5001'
    os.environ['WS_HOST'] = '0.0.0.0'
    os.environ['HEADLESS'] = 'False'  # Para ver el navegador
    os.environ['CHROME_PATH'] = chrome_path
    
    # Variables específicas para WSL
    if 'microsoft' in subprocess.getoutput('uname -r').lower():
        print("🐧 Detectado WSL - Configurando variables específicas")
        os.environ['DISPLAY'] = ':0'  # Para GUI si es necesario
        os.environ['CHROME_OPTIONS'] = '--no-sandbox --disable-dev-shm-usage --disable-gpu'
    
    print("\n🌐 Configuración:")
    print(f"   Puerto: {os.environ['WS_PORT']}")
    print(f"   Host: {os.environ['WS_HOST']}")
    print(f"   Headless: {os.environ['HEADLESS']}")
    print(f"   Chrome: {chrome_path}")
    print("=" * 60)
    
    try:
        # Iniciar servidor
        print("🔄 Importando módulos...")
        from real_websocket_server import socketio, app, logger
        
        logger.info("🎯 Servidor WebSocket REAL iniciado")
        logger.info("📱 Conectando con WhatsApp Web usando Selenium")
        logger.info("🔗 Endpoints disponibles:")
        logger.info(f"   - WebSocket: ws://localhost:5001/socket.io/")
        logger.info(f"   - Health: http://localhost:5001/health")
        logger.info(f"   - Stats: http://localhost:5001/stats")
        
        print("\n🌟 Servidor iniciado exitosamente!")
        print("🔗 Conecta desde el frontend a: ws://localhost:5001/socket.io/")
        print("⚡ Presiona Ctrl+C para detener")
        
        socketio.run(
            app,
            host='0.0.0.0',
            port=5001,
            debug=False,
            allow_unsafe_werkzeug=True
        )
        
    except Exception as e:
        print(f"❌ Error iniciando servidor: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    start_real_server()
