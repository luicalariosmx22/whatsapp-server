#!/usr/bin/env python3
"""
Diagnóstico específico para WhatsApp Web REAL
"""

import os
import sys
import requests
import subprocess
from datetime import datetime

def check_chrome_installation():
    """Verificar instalación de Chrome/Chromium"""
    print("🌐 VERIFICANDO CHROME/CHROMIUM")
    print("=" * 50)
    
    browsers = [
        ('google-chrome', 'Google Chrome'),
        ('chromium-browser', 'Chromium'),
        ('chrome', 'Chrome'),
        ('chromium', 'Chromium')
    ]
    
    found = False
    for cmd, name in browsers:
        try:
            result = subprocess.run([cmd, '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"✅ {name}: {result.stdout.strip()}")
                found = True
                break
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    
    if not found:
        print("❌ Chrome/Chromium no encontrado")
        print("📦 Instalación requerida:")
        print("   Ubuntu/Debian: sudo apt install google-chrome-stable")
        print("   WSL: Instala Chrome en Windows")
        return False
    
    return True

def check_selenium_deps():
    """Verificar dependencias de Selenium"""
    print("\n🤖 VERIFICANDO SELENIUM")
    print("=" * 50)
    
    required_packages = {
        'selenium': 'Selenium WebDriver',
        'webdriver_manager': 'WebDriver Manager',
        'PIL': 'Pillow (para imágenes)',
    }
    
    for package, description in required_packages.items():
        try:
            __import__(package)
            print(f"✅ {description}")
        except ImportError:
            print(f"❌ {description} - NO INSTALADO")
            print(f"   Instala con: pip install {package}")

def check_real_server():
    """Verificar servidor REAL de WhatsApp Web"""
    print("\n🔌 VERIFICANDO SERVIDOR REAL")
    print("=" * 50)
    
    try:
        response = requests.get('http://localhost:5001/health', timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            if data.get('type') == 'real_whatsapp_server':
                print("✅ Servidor REAL de WhatsApp Web activo")
                print(f"   Status: {data.get('status')}")
                print(f"   Selenium: {'✅' if data.get('selenium_ready') else '❌'}")
                print(f"   Sesiones activas: {data.get('sessions', {})}")
                return True
            else:
                print("⚠️ Servidor encontrado pero NO es la versión REAL")
                print("   Ejecuta: python start_real_whatsapp.py")
                return False
        else:
            print(f"⚠️ Servidor responde con código: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Servidor REAL no está ejecutándose")
        print("   Ejecuta: python start_real_whatsapp.py")
        return False
    except Exception as e:
        print(f"❌ Error verificando servidor: {e}")
        return False

def check_display():
    """Verificar display para GUI (importante en WSL)"""
    print("\n🖥️ VERIFICANDO DISPLAY")
    print("=" * 50)
    
    display = os.getenv('DISPLAY')
    if display:
        print(f"✅ DISPLAY configurado: {display}")
    else:
        print("⚠️ DISPLAY no configurado")
        print("   En WSL, instala VcXsrv o X410")
        print("   Configura: export DISPLAY=:0")
    
    # Verificar si es WSL
    try:
        with open('/proc/version', 'r') as f:
            version = f.read()
            if 'microsoft' in version.lower() or 'wsl' in version.lower():
                print("📝 Detectado WSL - Configuración especial requerida")
                print("   1. Instala VcXsrv en Windows")
                print("   2. Ejecuta VcXsrv con 'Disable access control'")
                print("   3. export DISPLAY=:0")
    except:
        pass

def test_selenium():
    """Probar Selenium básico"""
    print("\n🧪 PROBANDO SELENIUM")
    print("=" * 50)
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        
        print("✅ Imports de Selenium exitosos")
        
        # Configurar opciones de prueba
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        print("✅ Opciones de Chrome configuradas")
        
        # Intentar crear driver
        service = Service(ChromeDriverManager().install())
        print("✅ ChromeDriver descargado/encontrado")
        
        driver = webdriver.Chrome(service=service, options=options)
        print("✅ Driver de Chrome creado")
        
        # Prueba básica
        driver.get("https://www.google.com")
        title = driver.title
        print(f"✅ Navegación exitosa: {title}")
        
        driver.quit()
        print("✅ Driver cerrado correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de Selenium: {e}")
        return False

def main():
    """Función principal de diagnóstico"""
    print("🔍 DIAGNÓSTICO WHATSAPP WEB REAL")
    print("=" * 60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    all_ok = True
    
    # Verificar Chrome
    if not check_chrome_installation():
        all_ok = False
    
    # Verificar dependencias
    check_selenium_deps()
    
    # Verificar display
    check_display()
    
    # Probar Selenium
    if not test_selenium():
        all_ok = False
    
    # Verificar servidor
    if not check_real_server():
        all_ok = False
    
    print("\n🎯 RESULTADO FINAL")
    print("=" * 50)
    
    if all_ok:
        print("✅ Sistema listo para WhatsApp Web REAL")
        print("🚀 Ejecuta: python start_real_whatsapp.py")
    else:
        print("❌ Algunos problemas encontrados")
        print("📋 Revisa los errores arriba y corrige antes de continuar")
    
    print("\n📝 COMANDOS ÚTILES:")
    print("   Servidor real: python start_real_whatsapp.py")
    print("   Frontend: Navega a http://localhost:5000/panel_cliente_qr_whatsapp_web/")
    print("   Health check: curl http://localhost:5001/health")

if __name__ == '__main__':
    main()
