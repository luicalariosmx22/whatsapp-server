#!/usr/bin/env python3
"""
Prueba rápida de ChromeDriver
"""
import sys
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def test_chromedriver():
    print("🧪 PROBANDO CHROMEDRIVER")
    print("=" * 50)
    
    try:
        # Configurar opciones de Chrome
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--remote-debugging-port=9222')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36')
        
        print("✅ Opciones de Chrome configuradas")
        
        # Instalar ChromeDriver
        print("📥 Usando ChromeDriver del sistema...")
        service = Service("/usr/bin/chromedriver")
        print("✅ ChromeDriver del sistema configurado")
        
        # Crear driver
        print("🚀 Creando driver...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("✅ Driver creado exitosamente")
        
        # Probar navegación
        print("🌐 Navegando a página de prueba...")
        driver.get("https://www.google.com")
        title = driver.title
        print(f"✅ Título obtenido: {title}")
        
        # Cerrar driver
        driver.quit()
        print("✅ Driver cerrado correctamente")
        
        print("\n🎉 PRUEBA EXITOSA - ChromeDriver funcionando correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        return False

if __name__ == "__main__":
    success = test_chromedriver()
    sys.exit(0 if success else 1)
