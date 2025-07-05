#!/bin/bash
# Script para iniciar WhatsApp Web Real en terminal separada

echo "🚀 Configurando WhatsApp Web Real"
echo "=================================="

# Ir al directorio del proyecto
cd /mnt/c/Users/PC/PYTHON/Auraai2

# Activar entorno virtual
source venv/bin/activate

# Verificar que Nora está corriendo en puerto 5000
echo "🔍 Verificando Nora en puerto 5000..."
curl -s http://localhost:5000 > /dev/null && echo "✅ Nora corriendo" || echo "❌ Nora no responde"

# Instalar dependencias si faltan
echo "📦 Verificando dependencias..."
pip install flask flask-socketio flask-cors selenium webdriver-manager

# Iniciar servidor WhatsApp Web Real
echo "🎯 Iniciando WhatsApp Web Real en puerto 5001..."
python3 start_real_whatsapp.py
