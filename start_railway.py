#!/usr/bin/env python3
"""
Script para iniciar el servidor WebSocket REAL de WhatsApp Web en Railway
"""

import os
import sys
import signal
import subprocess

def setup_railway_environment():
    """Configurar entorno para Railway"""
    # Variables de entorno para Railway
    os.environ['WS_HOST'] = '0.0.0.0'
    os.environ['WS_PORT'] = str(os.environ.get('PORT', '5001'))
    os.environ['DEBUG'] = 'False'
    
    # Configurar display para headless
    os.environ['DISPLAY'] = ':99'
    
    print("🚀 Configurando entorno para Railway...")
    print(f"   Puerto: {os.environ.get('WS_PORT')}")
    print(f"   Host: {os.environ.get('WS_HOST')}")

def check_chrome_railway():
    """Verificar Chrome en Railway"""
    chrome_paths = [
        '/usr/bin/google-chrome',
        '/usr/bin/chromium-browser', 
        '/usr/bin/chromium',
        '/usr/bin/chrome',
        '/usr/bin/google-chrome-stable'
    ]
    
    for path in chrome_paths:
        try:
            result = subprocess.run([path, '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ Chrome encontrado en {path}: {result.stdout.strip()}")
                os.environ['CHROME_PATH'] = path
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    
    # Si no encontramos Chrome, intentar instalarlo
    print("⚠️  Chrome no encontrado, intentando configurar...")
    return install_chrome_railway()

def install_chrome_railway():
    """Instalar Chrome en Railway si no está disponible"""
    print("🔧 Intentando configurar Chrome para Railway...")
    
    try:
        # Verificar si tenemos chromium-browser
        result = subprocess.run(['which', 'chromium-browser'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            chrome_path = result.stdout.strip()
            print(f"✅ Chromium encontrado en: {chrome_path}")
            os.environ['CHROME_PATH'] = chrome_path
            return True
            
        # Verificar si tenemos google-chrome
        result = subprocess.run(['which', 'google-chrome'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            chrome_path = result.stdout.strip()
            print(f"✅ Google Chrome encontrado en: {chrome_path}")
            os.environ['CHROME_PATH'] = chrome_path
            return True
            
        print("❌ No se pudo encontrar Chrome en Railway")
        print("💡 Sugerencia: Agregar nixpacks.toml para instalar Chrome")
        return False
        
    except Exception as e:
        print(f"❌ Error verificando Chrome: {e}")
        return False

def main():
    """Función principal para Railway"""
    print("🚀 Iniciando servidor WebSocket REAL de WhatsApp Web")
    print("=" * 60)
    
    # Configurar entorno
    setup_railway_environment()
    
    # Verificar Chrome
    chrome_available = check_chrome_railway()
    if not chrome_available:
        print("❌ Error: Chrome no está disponible")
        print("🔧 Opciones:")
        print("   1. Usar nixpacks.toml para instalar Chrome")
        print("   2. Configurar buildpack de Chrome")
        print("   3. Usar modo sin navegador (solo API)")
        
        # Continuar sin Chrome en modo API
        print("⚠️  Continuando en modo API sin navegador...")
        os.environ['NO_CHROME_MODE'] = 'true'
    
    print("🌐 Configuración:")
    print(f"   Puerto: {os.environ.get('WS_PORT')}")
    print(f"   Host: {os.environ.get('WS_HOST')}")
    print(f"   Headless: True")
    print("=" * 60)
    
    # Importar y ejecutar servidor
    try:
        from real_websocket_server import app, socketio
        
        print("🎯 Servidor WebSocket REAL iniciado")
        print("📱 Conectando con WhatsApp Web usando Selenium")
        print("🔗 Endpoints disponibles:")
        print(f"   - WebSocket: ws://0.0.0.0:{os.environ.get('WS_PORT')}/socket.io/")
        print(f"   - Health: http://0.0.0.0:{os.environ.get('WS_PORT')}/health")
        print(f"   - Stats: http://0.0.0.0:{os.environ.get('WS_PORT')}/stats")
        
        socketio.run(
            app,
            host=os.environ.get('WS_HOST'),
            port=int(os.environ.get('WS_PORT')),
            debug=False,
            allow_unsafe_werkzeug=True
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error iniciando servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
