#!/usr/bin/env python3
"""
Script para verificar y diagnosticar el servidor WebSocket
"""

import requests
import socket
import subprocess
import sys
import os
import time

def verificar_puerto(host, puerto):
    """Verificar si un puerto está abierto"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(3)
            result = sock.connect_ex((host, puerto))
            return result == 0
    except Exception as e:
        print(f"❌ Error al verificar puerto {puerto}: {e}")
        return False

def verificar_health_endpoint(host, puerto):
    """Verificar el endpoint de health del WebSocket"""
    try:
        url = f"http://{host}:{puerto}/health"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health endpoint OK: {data}")
            return True
        else:
            print(f"❌ Health endpoint error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error al verificar health endpoint: {e}")
        return False

def iniciar_servidor_websocket():
    """Iniciar el servidor WebSocket"""
    try:
        print("🚀 Iniciando servidor WebSocket...")
        
        # Cambiar al directorio del proyecto
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        
        # Ejecutar el servidor en background
        subprocess.Popen([
            sys.executable, 
            "websocket_server.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Esperar un poco para que inicie
        time.sleep(3)
        
        return True
    except Exception as e:
        print(f"❌ Error al iniciar servidor WebSocket: {e}")
        return False

def main():
    host = "localhost"
    puerto = 5001
    
    print("🔍 Verificando servidor WebSocket...")
    print(f"📍 Host: {host}")
    print(f"🔌 Puerto: {puerto}")
    print("-" * 50)
    
    # 1. Verificar puerto
    print("1️⃣ Verificando puerto...")
    if verificar_puerto(host, puerto):
        print(f"✅ Puerto {puerto} está abierto")
        
        # 2. Verificar health endpoint
        print("2️⃣ Verificando health endpoint...")
        if verificar_health_endpoint(host, puerto):
            print("🎉 Servidor WebSocket funcionando correctamente!")
            return True
        else:
            print("⚠️ Servidor responde pero health endpoint falla")
            return False
    else:
        print(f"❌ Puerto {puerto} está cerrado")
        
        # 3. Intentar iniciar servidor
        print("3️⃣ Intentando iniciar servidor WebSocket...")
        if iniciar_servidor_websocket():
            print("⏳ Esperando que el servidor inicie...")
            time.sleep(5)
            
            # Verificar nuevamente
            if verificar_puerto(host, puerto):
                print("✅ Servidor WebSocket iniciado exitosamente!")
                return True
            else:
                print("❌ No se pudo iniciar el servidor WebSocket")
                return False
        else:
            print("❌ Error al iniciar servidor WebSocket")
            return False

if __name__ == "__main__":
    if main():
        print("\n🎯 RESUMEN: Servidor WebSocket OK")
        print("💡 Ahora puedes usar el módulo WhatsApp Web QR")
    else:
        print("\n❌ RESUMEN: Problemas con servidor WebSocket")
        print("💡 Revisa los logs para más detalles")
        sys.exit(1)
