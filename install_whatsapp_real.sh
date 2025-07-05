#!/bin/bash
"""
Script de instalación para WhatsApp Web Real
"""

echo "🚀 Instalando dependencias para WhatsApp Web Real..."

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    echo "✅ Activando entorno virtual..."
    source venv/bin/activate
fi

# Instalar dependencias principales
echo "📦 Instalando dependencias principales..."
pip install flask flask-socketio flask-cors python-socketio eventlet

# Instalar Selenium y WebDriver
echo "🌐 Instalando Selenium y WebDriver..."
pip install selenium webdriver-manager

# Instalar utilidades
echo "🛠️ Instalando utilidades..."
pip install qrcode[pil] requests python-dotenv pillow

# Instalar opcionales
echo "📊 Instalando opcionales..."
pip install redis colorama rich

echo "✅ Instalación completada!"
echo ""
echo "🔧 Para usar WhatsApp Web Real:"
echo "1. Ejecuta: python websocket_server_real.py"
echo "2. El servidor se iniciará en puerto 5001"
echo "3. Selenium abrirá Chrome automáticamente"
echo ""
echo "⚠️ Nota: Necesitas tener Chrome instalado"
