#!/usr/bin/env python3
"""
Script de diagnóstico para verificar el estado del servidor en Railway
"""

import requests
import json
import time

def check_railway_server():
    """Verificar estado del servidor en Railway"""
    
    base_url = "https://whatsapp-server-production-8f61.up.railway.app"
    
    print("🔍 Diagnóstico del servidor en Railway")
    print("=" * 60)
    print(f"🌐 URL: {base_url}")
    print("=" * 60)
    
    # Lista de rutas a probar
    routes = [
        "/",
        "/health", 
        "/stats",
        "/docs",
        "/favicon.ico"
    ]
    
    for route in routes:
        url = f"{base_url}{route}"
        print(f"\n🧪 Probando: {route}")
        
        try:
            response = requests.get(url, timeout=10)
            
            print(f"   📊 Status Code: {response.status_code}")
            print(f"   📏 Content Length: {len(response.text)} bytes")
            print(f"   📄 Content Type: {response.headers.get('content-type', 'N/A')}")
            
            if response.status_code == 200:
                try:
                    # Intentar parsear como JSON
                    data = response.json()
                    print(f"   ✅ JSON Response:")
                    for key, value in data.items():
                        if isinstance(value, str) and len(value) > 50:
                            print(f"      {key}: {value[:50]}...")
                        else:
                            print(f"      {key}: {value}")
                except:
                    # Si no es JSON, mostrar contenido HTML
                    content = response.text.strip()
                    if content:
                        print(f"   📄 HTML/Text Content (first 200 chars):")
                        print(f"      {content[:200]}...")
                    else:
                        print(f"   📄 Empty response")
            else:
                print(f"   ❌ Error Response:")
                print(f"      {response.text[:200]}...")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Connection Error: No se pudo conectar")
        except requests.exceptions.Timeout:
            print(f"   ⏰ Timeout: Respuesta demorada")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    
    # Verificar si el servidor está corriendo
    try:
        response = requests.get(base_url, timeout=5)
        if "Not Found" in response.text:
            print("⚠️  DIAGNÓSTICO: El servidor está corriendo pero faltan las rutas")
            print("💡 SOLUCIÓN: El deploy no incluye las rutas nuevas")
        else:
            print("✅ DIAGNÓSTICO: Servidor respondiendo correctamente")
    except:
        print("❌ DIAGNÓSTICO: Servidor no responde o no está corriendo")
    
    print("\n🔧 POSIBLES SOLUCIONES:")
    print("1. Verificar que el deploy más reciente se haya aplicado")
    print("2. Revisar logs en Railway para errores")
    print("3. Forzar redeploy en Railway")
    print("4. Verificar que start_railway.py esté usando el archivo correcto")

if __name__ == "__main__":
    check_railway_server()
