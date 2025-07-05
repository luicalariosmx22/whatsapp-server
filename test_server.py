#!/usr/bin/env python3
"""
Script para probar el servidor WebSocket localmente
"""

import requests
import time
import json

def test_server(base_url="http://localhost:5001"):
    """Probar todas las rutas del servidor"""
    
    print(f"🧪 Probando servidor en: {base_url}")
    print("=" * 50)
    
    # Probar ruta principal
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ GET / - Status: {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   📋 Servicio: {data.get('service', 'N/A')}")
                print(f"   📊 Estado: {data.get('status', 'N/A')}")
            except:
                print("   📄 Página HTML servida correctamente")
    except Exception as e:
        print(f"❌ GET / - Error: {e}")
    
    # Probar health
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ GET /health - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   🩺 Salud: {data.get('status', 'N/A')}")
    except Exception as e:
        print(f"❌ GET /health - Error: {e}")
    
    # Probar stats
    try:
        response = requests.get(f"{base_url}/stats")
        print(f"✅ GET /stats - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   📊 Sesiones: {data.get('sessions', {}).get('total_sessions', 0)}")
    except Exception as e:
        print(f"❌ GET /stats - Error: {e}")
    
    # Probar docs
    try:
        response = requests.get(f"{base_url}/docs")
        print(f"✅ GET /docs - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   📚 Título: {data.get('title', 'N/A')}")
    except Exception as e:
        print(f"❌ GET /docs - Error: {e}")
    
    # Probar favicon
    try:
        response = requests.get(f"{base_url}/favicon.ico")
        print(f"✅ GET /favicon.ico - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ GET /favicon.ico - Error: {e}")
    
    print("=" * 50)
    print("🎉 Pruebas completadas")

if __name__ == "__main__":
    # Probar servidor local
    test_server("http://localhost:5001")
    
    # Si tienes la URL de Railway, descomenta la siguiente línea
    # test_server("https://tu-app.railway.app")
