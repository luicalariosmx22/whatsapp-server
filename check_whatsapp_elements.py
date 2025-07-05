#!/usr/bin/env python3
"""
Script para verificar elementos de WhatsApp Web después de autenticación
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

def check_whatsapp_elements():
    # Configurar Chrome
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36')
    
    service = Service('/usr/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        print("Navegando a WhatsApp Web...")
        driver.get("https://web.whatsapp.com")
        
        print("Esperando 30 segundos para que puedas autenticarte...")
        time.sleep(30)
        
        print("\n=== ELEMENTOS ENCONTRADOS ===")
        
        # Buscar elementos comunes de WhatsApp Web autenticado
        selectors = [
            "[data-testid='chat-list-search']",
            "[data-testid='search']", 
            "[data-testid='chatlist-search']",
            "input[placeholder*='Search']",
            "input[placeholder*='Buscar']",
            "[aria-label*='Search']",
            "[aria-label*='Buscar']",
            "._3uMse",  # Clase común del chat list
            "._2_e0y",  # Otra clase común
            "#main",
            ".app",
            "._1jJ70"  # Sidebar
        ]
        
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"✅ ENCONTRADO: {selector} ({len(elements)} elementos)")
                else:
                    print(f"❌ NO ENCONTRADO: {selector}")
            except Exception as e:
                print(f"❌ ERROR con {selector}: {e}")
        
        # Verificar título de la página
        print(f"\n=== TÍTULO ===")
        print(f"Título: {driver.title}")
        
        # Verificar URL
        print(f"\n=== URL ===")
        print(f"URL: {driver.current_url}")
        
        input("Presiona Enter para cerrar...")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    check_whatsapp_elements()
