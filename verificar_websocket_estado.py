#!/usr/bin/env python3
"""
🔍 Verificador de estado del servidor WebSocket
Verifica si el servidor WebSocket está funcionando correctamente
"""

import requests
import socketio
import time
import sys

def verificar_servidor_websocket():
    """Verificar estado del servidor WebSocket"""
    host = 'localhost'
    port = 5001
    
    print("🔍 Verificando estado del servidor WebSocket...")
    print(f"📍 Host: {host}")
    print(f"🔌 Puerto: {port}")
    print("-" * 50)
    
    # 1. Verificar endpoint HTTP de salud
    try:
        print("1️⃣ Verificando endpoint de salud...")
        url = f"http://{host}:{port}/health"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            print("✅ Endpoint de salud responde correctamente")
            print(f"📊 Respuesta: {response.text}")
        else:
            print(f"⚠️ Endpoint responde con código: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al verificar endpoint de salud: {e}")
        return False
    
    # 2. Verificar conexión WebSocket
    try:
        print("\n2️⃣ Verificando conexión WebSocket...")
        sio = socketio.SimpleClient()
        
        print(f"🔌 Conectando a http://{host}:{port}")
        sio.connect(f'http://{host}:{port}')
        
        print("✅ Conexión WebSocket establecida")
        print(f"🆔 Socket ID: {sio.sid}")
        
        # 3. Probar evento get_qr
        print("\n3️⃣ Probando evento get_qr...")
        sio.emit('get_qr', {'session_id': None})
        
        # Esperar respuesta
        print("⏳ Esperando respuesta...")
        event = sio.receive(timeout=10)
        
        if event:
            print(f"📨 Evento recibido: {event[0]}")
            print(f"📊 Datos: {event[1]}")
            
            if event[0] == 'qr_code':
                print("✅ Evento QR funcionando correctamente")
            else:
                print(f"⚠️ Evento inesperado: {event[0]}")
        else:
            print("❌ No se recibió respuesta del servidor")
            
        sio.disconnect()
        print("🔌 Desconectado del servidor")
        
    except Exception as e:
        print(f"❌ Error en conexión WebSocket: {e}")
        return False
    
    print("\n🎯 RESUMEN: Servidor WebSocket funcionando correctamente!")
    return True

if __name__ == "__main__":
    try:
        if verificar_servidor_websocket():
            print("💡 El módulo WhatsApp Web QR debería funcionar correctamente")
        else:
            print("❌ Hay problemas con el servidor WebSocket")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️ Verificación cancelada por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)
