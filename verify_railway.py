#!/usr/bin/env python3
"""
Script de verificación para Railway - Probar Chrome y dependencias
"""

import os
import sys
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_chrome_installation():
    """Verificar instalación de Chrome"""
    logger.info("🔍 Verificando Chrome...")
    
    chrome_paths = [
        '/usr/bin/google-chrome',
        '/usr/bin/chromium-browser',
        '/usr/bin/chromium',
        '/usr/bin/chrome',
        '/usr/bin/google-chrome-stable'
    ]
    
    for path in chrome_paths:
        if os.path.exists(path):
            try:
                result = subprocess.run([path, '--version'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    logger.info(f"✅ Chrome encontrado: {path}")
                    logger.info(f"   Versión: {result.stdout.strip()}")
                    return True
            except subprocess.TimeoutExpired:
                logger.warning(f"⚠️  Timeout verificando {path}")
            except Exception as e:
                logger.error(f"❌ Error verificando {path}: {e}")
    
    logger.error("❌ Chrome no encontrado en ninguna ruta")
    return False

def check_chromedriver():
    """Verificar ChromeDriver"""
    logger.info("🔍 Verificando ChromeDriver...")
    
    driver_paths = [
        '/usr/bin/chromedriver',
        '/usr/local/bin/chromedriver'
    ]
    
    for path in driver_paths:
        if os.path.exists(path):
            try:
                result = subprocess.run([path, '--version'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    logger.info(f"✅ ChromeDriver encontrado: {path}")
                    logger.info(f"   Versión: {result.stdout.strip()}")
                    return True
            except subprocess.TimeoutExpired:
                logger.warning(f"⚠️  Timeout verificando {path}")
            except Exception as e:
                logger.error(f"❌ Error verificando {path}: {e}")
    
    logger.error("❌ ChromeDriver no encontrado")
    return False

def check_python_dependencies():
    """Verificar dependencias Python"""
    logger.info("🔍 Verificando dependencias Python...")
    
    required_packages = [
        'selenium',
        'flask',
        'flask-socketio',
        'gevent',
        'qrcode',
        'pillow'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            logger.info(f"✅ {package} instalado")
        except ImportError:
            missing_packages.append(package)
            logger.error(f"❌ {package} no encontrado")
    
    return len(missing_packages) == 0

def check_environment():
    """Verificar variables de entorno"""
    logger.info("🔍 Verificando variables de entorno...")
    
    env_vars = {
        'PORT': os.getenv('PORT', 'No configurado'),
        'RAILWAY_ENVIRONMENT': os.getenv('RAILWAY_ENVIRONMENT', 'No configurado'),
        'WS_HOST': os.getenv('WS_HOST', 'No configurado'),
        'WS_PORT': os.getenv('WS_PORT', 'No configurado'),
        'DEBUG': os.getenv('DEBUG', 'No configurado'),
        'HEADLESS': os.getenv('HEADLESS', 'No configurado'),
        'NO_CHROME_MODE': os.getenv('NO_CHROME_MODE', 'No configurado')
    }
    
    for var, value in env_vars.items():
        logger.info(f"   {var}: {value}")
    
    return True

def test_selenium_basic():
    """Probar Selenium básico"""
    logger.info("🔍 Probando Selenium básico...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        
        # Configurar Chrome headless
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
        # Buscar Chrome
        chrome_paths = [
            '/usr/bin/google-chrome',
            '/usr/bin/chromium-browser',
            '/usr/bin/chromium'
        ]
        
        chrome_path = None
        for path in chrome_paths:
            if os.path.exists(path):
                chrome_path = path
                break
        
        if not chrome_path:
            logger.error("❌ Chrome no encontrado para prueba")
            return False
        
        chrome_options.binary_location = chrome_path
        
        # Buscar ChromeDriver
        driver_paths = [
            '/usr/bin/chromedriver',
            '/usr/local/bin/chromedriver'
        ]
        
        driver_path = None
        for path in driver_paths:
            if os.path.exists(path):
                driver_path = path
                break
        
        if not driver_path:
            logger.error("❌ ChromeDriver no encontrado para prueba")
            return False
        
        service = Service(driver_path)
        
        # Crear driver
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Probar navegación básica
        driver.get("https://www.google.com")
        title = driver.title
        driver.quit()
        
        logger.info(f"✅ Selenium funcionando - Página cargada: {title}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error probando Selenium: {e}")
        return False

def main():
    """Función principal de verificación"""
    logger.info("🚀 Iniciando verificación completa...")
    logger.info("=" * 50)
    
    checks = [
        ("Chrome", check_chrome_installation),
        ("ChromeDriver", check_chromedriver),
        ("Dependencias Python", check_python_dependencies),
        ("Variables de entorno", check_environment),
        ("Selenium básico", test_selenium_basic)
    ]
    
    results = []
    for check_name, check_func in checks:
        logger.info(f"\n📋 {check_name}:")
        result = check_func()
        results.append((check_name, result))
        logger.info(f"   Resultado: {'✅ PASS' if result else '❌ FAIL'}")
    
    logger.info("\n" + "=" * 50)
    logger.info("📊 RESUMEN DE VERIFICACIÓN:")
    
    all_passed = True
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"   {check_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        logger.info("\n🎉 ¡Todas las verificaciones pasaron!")
        logger.info("🚀 El servidor debería funcionar correctamente en Railway")
    else:
        logger.error("\n⚠️  Algunas verificaciones fallaron")
        logger.error("🔧 Revisa los logs arriba para más detalles")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
