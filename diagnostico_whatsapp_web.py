#!/usr/bin/env python3
"""
Script de diagnóstico para el módulo WhatsApp Web QR
"""

import os
import sys
import json
import requests
import subprocess
import time
from datetime import datetime

def check_system_info():
    """Verificar información del sistema"""
    print("🖥️  INFORMACIÓN DEL SISTEMA")
    print("=" * 50)
    
    try:
        # Sistema operativo
        print(f"OS: {os.name}")
        print(f"Python: {sys.version}")
        print(f"Directorio actual: {os.getcwd()}")
        
        # Verificar puertos
        print("\n🔌 PUERTOS")
        print("-" * 20)
        
        # Puerto Flask principal (probablemente 5000)
        try:
            response = requests.get('http://localhost:5000/health', timeout=5)
            print(f"✅ Puerto 5000 (Flask): {response.status_code}")
        except:
            print("❌ Puerto 5000 (Flask): No disponible")
        
        # Puerto WebSocket (5001)
        try:
            response = requests.get('http://localhost:5001/health', timeout=5)
            print(f"✅ Puerto 5001 (WebSocket): {response.status_code}")
        except:
            print("❌ Puerto 5001 (WebSocket): No disponible")
        
    except Exception as e:
        print(f"❌ Error verificando sistema: {e}")

def check_files():
    """Verificar archivos necesarios"""
    print("\n📁 ARCHIVOS NECESARIOS")
    print("=" * 50)
    
    required_files = [
        'websocket_server.py',
        'clientes/aura/templates/panel_cliente_qr_whatsapp_web/index_websocket.html',
        'clientes/aura/templates/base_cliente.html',
        'clientes/aura/routes/panel_cliente_qr_whatsapp_web/__init__.py'
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"✅ {file_path} ({size} bytes)")
        else:
            print(f"❌ {file_path} - NO ENCONTRADO")

def check_dependencies():
    """Verificar dependencias de Python"""
    print("\n📦 DEPENDENCIAS DE PYTHON")
    print("=" * 50)
    
    required_packages = [
        'flask',
        'flask-socketio',
        'flask-cors',
        'qrcode',
        'python-socketio',
        'requests',
        'gunicorn'
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - NO INSTALADO")

def check_websocket_server():
    """Verificar servidor WebSocket"""
    print("\n🔌 SERVIDOR WEBSOCKET")
    print("=" * 50)
    
    try:
        # Verificar endpoint de salud
        response = requests.get('http://localhost:5001/health', timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Servidor WebSocket activo")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Sesiones: {data.get('sessions', {})}")
        else:
            print(f"⚠️  Servidor WebSocket responde con código: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Servidor WebSocket no está ejecutándose")
        print("   Ejecuta: python start_websocket_server.py")
    except Exception as e:
        print(f"❌ Error verificando WebSocket: {e}")

def check_routes():
    """Verificar rutas de Flask"""
    print("\n🛣️  RUTAS DE FLASK")
    print("=" * 50)
    
    routes_to_check = [
        'http://localhost:5000/panel_cliente_qr_whatsapp_web/',
        'http://localhost:5000/health',
        'http://localhost:5000/panel_cliente_qr_whatsapp_web/index_websocket'
    ]
    
    for route in routes_to_check:
        try:
            response = requests.get(route, timeout=5)
            print(f"✅ {route}: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"❌ {route}: Servidor no disponible")
        except Exception as e:
            print(f"⚠️  {route}: {e}")

def check_frontend():
    """Verificar archivos del frontend"""
    print("\n🎨 FRONTEND")
    print("=" * 50)
    
    frontend_file = 'clientes/aura/templates/panel_cliente_qr_whatsapp_web/index_websocket.html'
    
    if os.path.exists(frontend_file):
        print(f"✅ Archivo frontend encontrado")
        
        # Verificar contenido crítico
        with open(frontend_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        checks = [
            ('Socket.IO', 'socket.io' in content),
            ('Funciones JS', 'function' in content),
            ('Eventos Socket', 'socket.on' in content),
            ('Botones', 'btn' in content),
            ('QR Section', 'qr-section' in content)
        ]
        
        for check_name, result in checks:
            if result:
                print(f"✅ {check_name}: OK")
            else:
                print(f"❌ {check_name}: FALTANTE")
    else:
        print(f"❌ Archivo frontend no encontrado: {frontend_file}")

def generate_report():
    """Generar reporte de diagnóstico"""
    print("\n📊 GENERANDO REPORTE")
    print("=" * 50)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f'diagnostico_whatsapp_web_{timestamp}.txt'
    
    try:
        # Capturar salida
        original_stdout = sys.stdout
        with open(report_file, 'w', encoding='utf-8') as f:
            sys.stdout = f
            
            print(f"DIAGNÓSTICO WHATSAPP WEB QR - {datetime.now()}")
            print("=" * 60)
            
            check_system_info()
            check_files()
            check_dependencies()
            check_websocket_server()
            check_routes()
            check_frontend()
            
        sys.stdout = original_stdout
        print(f"✅ Reporte generado: {report_file}")
        
    except Exception as e:
        print(f"❌ Error generando reporte: {e}")

def main():
    """Función principal"""
    print("🔍 DIAGNÓSTICO WHATSAPP WEB QR")
    print("=" * 60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    check_system_info()
    check_files()
    check_dependencies()
    check_websocket_server()
    check_routes()
    check_frontend()
    
    print("\n🎯 RECOMENDACIONES")
    print("=" * 50)
    print("1. Asegúrate de que el servidor WebSocket esté ejecutándose:")
    print("   python start_websocket_server.py")
    print("\n2. Verifica que Flask esté corriendo en el puerto 5000")
    print("\n3. Abre F12 en el navegador para ver logs de JavaScript")
    print("\n4. Revisa los logs del servidor para errores")
    
    # Generar reporte
    generate_report()

if __name__ == '__main__':
    main()
