#!/usr/bin/env python3
"""
Script completo para probar el funcionamiento del WebSocket WhatsApp QR
"""

import socketio
import time
import json
import requests
from datetime import datetime

def probar_websocket():
    print("🚀 Iniciando prueba completa del WebSocket WhatsApp QR")
    print("=" * 60)
    
    # Configuración
    host = 'localhost'
    port = 5001
    url = f'http://{host}:{port}'
    
    # 1. Verificar que el servidor esté corriendo
    print("1️⃣ Verificando servidor...")
    try:
        response = requests.get(f'{url}/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Servidor responde: {data['status']}")
            print(f"📊 Sesiones activas: {data['sessions']['total_sessions']}")
        else:
            print(f"❌ Servidor responde con error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ No se puede conectar al servidor: {e}")
        return False
    
    # 2. Conectar Socket.IO
    print("\n2️⃣ Conectando Socket.IO...")
    sio = socketio.Client()
    
    eventos_recibidos = []
    session_id = None
    
    @sio.event
    def connect():
        print("✅ Conectado al WebSocket")
    
    @sio.event
    def connected(data):
        print(f"🔗 Evento 'connected': {data}")
        eventos_recibidos.append(('connected', data))
    
    @sio.event
    def qr_code(data):
        nonlocal session_id
        print(f"📱 Evento 'qr_code': Session {data.get('session_id')}")
        print(f"📊 QR Data length: {len(data.get('qr_data', ''))}")
        session_id = data.get('session_id')
        eventos_recibidos.append(('qr_code', data))
    
    @sio.event
    def authenticated(data):
        print(f"🎉 Evento 'authenticated': {data}")
        eventos_recibidos.append(('authenticated', data))
    
    @sio.event
    def status(data):
        print(f"📊 Evento 'status': {data}")
        eventos_recibidos.append(('status', data))
    
    @sio.event
    def error(data):
        print(f"❌ Evento 'error': {data}")
        eventos_recibidos.append(('error', data))
    
    @sio.event
    def disconnect():
        print("🔌 Desconectado del WebSocket")
    
    try:
        # Conectar
        sio.connect(url)
        time.sleep(2)
        
        # 3. Solicitar QR
        print("\n3️⃣ Solicitando código QR...")
        sio.emit('get_qr', {})
        time.sleep(3)
        
        # 4. Verificar estado
        if session_id:
            print("\n4️⃣ Verificando estado de sesión...")
            sio.emit('get_status', {'session_id': session_id})
            time.sleep(2)
        
        # 5. Esperar autenticación simulada
        print("\n5️⃣ Esperando autenticación simulada (máximo 20 segundos)...")
        tiempo_espera = 0
        autenticado = False
        
        while tiempo_espera < 20 and not autenticado:
            time.sleep(1)
            tiempo_espera += 1
            
            # Verificar si se recibió evento de autenticación
            for evento, data in eventos_recibidos:
                if evento == 'authenticated':
                    autenticado = True
                    break
            
            if tiempo_espera % 5 == 0:
                print(f"⏳ Esperando... {tiempo_espera}s")
        
        # 6. Desconectar
        if session_id:
            print("\n6️⃣ Desconectando WhatsApp...")
            sio.emit('disconnect_whatsapp', {'session_id': session_id})
            time.sleep(2)
        
        sio.disconnect()
        
        # 7. Resumen
        print("\n" + "=" * 60)
        print("📋 RESUMEN DE LA PRUEBA")
        print("=" * 60)
        
        print(f"🔗 Conexión establecida: ✅")
        print(f"📱 QR generado: {'✅' if session_id else '❌'}")
        print(f"🎉 Autenticación simulada: {'✅' if autenticado else '❌'}")
        print(f"📊 Eventos recibidos: {len(eventos_recibidos)}")
        
        print("\n📨 Eventos recibidos:")
        for i, (evento, data) in enumerate(eventos_recibidos, 1):
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"  {i}. [{timestamp}] {evento}: {data.get('message', 'Sin mensaje')}")
        
        if session_id and autenticado:
            print("\n🎯 RESULTADO: ✅ PRUEBA EXITOSA")
            print("💡 El módulo WhatsApp Web QR funciona correctamente")
        else:
            print("\n🎯 RESULTADO: ⚠️ PRUEBA PARCIAL")
            print("💡 Revisa los logs para identificar problemas")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        return False
    
    finally:
        if sio.connected:
            sio.disconnect()

if __name__ == "__main__":
    try:
        probar_websocket()
    except KeyboardInterrupt:
        print("\n🛑 Prueba interrumpida por el usuario")
    except Exception as e:
        print(f"❌ Error crítico: {e}")
