#!/usr/bin/env python3
"""
Script de prueba para el servidor WebSocket de WhatsApp Web
"""

import time
import json
import logging
from websocket_server import WhatsAppWebSocketManager, socketio, app

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_websocket_server():
    """Probar funcionalidad del servidor WebSocket"""
    
    print("🧪 Iniciando pruebas del servidor WebSocket...")
    
    # Crear manager
    manager = WhatsAppWebSocketManager()
    
    # Prueba 1: Crear sesión
    print("\n📋 Prueba 1: Crear sesión")
    session_id = manager.create_session('test_client_001')
    print(f"✅ Sesión creada: {session_id}")
    
    # Prueba 2: Obtener sesión
    print("\n📋 Prueba 2: Obtener sesión")
    session = manager.get_session(session_id)
    print(f"✅ Sesión obtenida: {session['status']}")
    
    # Prueba 3: Generar QR
    print("\n📋 Prueba 3: Generar código QR")
    qr_data = manager.generate_qr_code(session_id)
    print(f"✅ QR generado: {qr_data[:50]}...")
    
    # Prueba 4: Verificar estado
    print("\n📋 Prueba 4: Verificar estado después de QR")
    session = manager.get_session(session_id)
    print(f"✅ Estado: {session['status']}")
    print(f"✅ QR disponible: {'qr_code' in session}")
    
    # Prueba 5: Estadísticas
    print("\n📋 Prueba 5: Estadísticas")
    stats = manager.get_active_sessions()
    print(f"✅ Estadísticas: {stats}")
    
    # Esperar autenticación simulada
    print("\n⏳ Esperando autenticación simulada (15 segundos)...")
    time.sleep(16)
    
    # Prueba 6: Verificar autenticación
    print("\n📋 Prueba 6: Verificar autenticación")
    session = manager.get_session(session_id)
    print(f"✅ Estado final: {session['status']}")
    print(f"✅ Autenticado: {session.get('authenticated', False)}")
    
    # Prueba 7: Limpieza
    print("\n📋 Prueba 7: Limpieza")
    manager.remove_session(session_id)
    stats = manager.get_active_sessions()
    print(f"✅ Estadísticas después de limpieza: {stats}")
    
    print("\n🎉 Todas las pruebas completadas exitosamente!")

def test_server_endpoints():
    """Probar endpoints HTTP del servidor"""
    
    print("\n🌐 Probando endpoints HTTP...")
    
    with app.test_client() as client:
        # Probar /health
        response = client.get('/health')
        print(f"✅ /health: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"   Status: {data['status']}")
            print(f"   Sesiones: {data['sessions']}")
        
        # Probar /stats
        response = client.get('/stats')
        print(f"✅ /stats: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"   Servidor: {data['server_info']}")

if __name__ == '__main__':
    print("🚀 Iniciando pruebas del servidor WebSocket de WhatsApp Web")
    print("=" * 60)
    
    try:
        # Probar funcionalidad del manager
        test_websocket_server()
        
        # Probar endpoints HTTP
        test_server_endpoints()
        
    except Exception as e:
        logger.error(f"❌ Error durante las pruebas: {e}")
        print(f"❌ Error durante las pruebas: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Pruebas terminadas")
