#!/usr/bin/env python3
"""
Script de inicio alternativo para Railway con mejor manejo de errores
"""

import os
import sys
import subprocess
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_environment():
    """Configurar entorno para Railway"""
    os.environ['WS_HOST'] = '0.0.0.0'
    os.environ['WS_PORT'] = str(os.environ.get('PORT', '8080'))
    os.environ['DEBUG'] = 'False'
    os.environ['DISPLAY'] = ':99'
    
    logger.info("🚀 Configurando entorno para Railway...")
    logger.info(f"   Puerto: {os.environ.get('WS_PORT')}")
    logger.info(f"   Host: {os.environ.get('WS_HOST')}")

def find_chrome():
    """Buscar Chrome en el sistema"""
    chrome_paths = [
        '/usr/bin/google-chrome',
        '/usr/bin/google-chrome-stable',
        '/usr/bin/chromium-browser',
        '/usr/bin/chromium',
        '/usr/bin/chrome'
    ]
    
    for path in chrome_paths:
        if os.path.exists(path):
            logger.info(f"✅ Chrome encontrado en: {path}")
            os.environ['CHROME_PATH'] = path
            return path
    
    logger.warning("⚠️ Chrome no encontrado - continuando en modo API")
    os.environ['NO_CHROME_MODE'] = 'true'
    return None

def find_chromedriver():
    """Buscar ChromeDriver en el sistema"""
    driver_paths = [
        '/usr/local/bin/chromedriver',
        '/usr/bin/chromedriver'
    ]
    
    for path in driver_paths:
        if os.path.exists(path):
            logger.info(f"✅ ChromeDriver encontrado en: {path}")
            return path
    
    logger.warning("⚠️ ChromeDriver no encontrado")
    return None

def start_server():
    """Iniciar el servidor WebSocket"""
    try:
        logger.info("🚀 Iniciando servidor WebSocket...")
        
        # Importar y ejecutar servidor
        from real_websocket_server import app, socketio
        
        logger.info("🎯 Servidor WebSocket iniciado exitosamente")
        logger.info("📱 Endpoints disponibles:")
        logger.info(f"   - WebSocket: ws://0.0.0.0:{os.environ.get('WS_PORT')}/socket.io/")
        logger.info(f"   - Health: http://0.0.0.0:{os.environ.get('WS_PORT')}/health")
        logger.info(f"   - Stats: http://0.0.0.0:{os.environ.get('WS_PORT')}/stats")
        
        socketio.run(
            app,
            host=os.environ.get('WS_HOST'),
            port=int(os.environ.get('WS_PORT')),
            debug=False,
            allow_unsafe_werkzeug=True
        )
        
    except ImportError as e:
        logger.error(f"❌ Error importando servidor: {e}")
        logger.error("💡 Asegúrate de que todos los archivos estén presentes")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error iniciando servidor: {e}")
        sys.exit(1)

def main():
    """Función principal"""
    logger.info("🚀 Iniciando WhatsApp Web Server en Railway")
    logger.info("=" * 60)
    
    # Configurar entorno
    setup_environment()
    
    # Buscar Chrome (opcional)
    chrome_path = find_chrome()
    
    # Buscar ChromeDriver (opcional)
    driver_path = find_chromedriver()
    
    # Mostrar estado
    logger.info("=" * 60)
    logger.info("📊 Estado de la configuración:")
    logger.info(f"   Chrome: {'✅ Disponible' if chrome_path else '⚠️ No disponible (modo API)'}")
    logger.info(f"   ChromeDriver: {'✅ Disponible' if driver_path else '⚠️ No disponible'}")
    logger.info(f"   Modo: {'WhatsApp Web Real' if chrome_path and driver_path else 'API con QR simulado'}")
    logger.info("=" * 60)
    
    # Iniciar servidor
    start_server()

if __name__ == "__main__":
    main()
