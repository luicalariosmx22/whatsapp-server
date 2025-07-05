@echo off
REM Script para ejecutar el servidor WebSocket de WhatsApp Web en Windows

REM Configuración
set WS_PORT=5001
set WS_HOST=0.0.0.0
set DEBUG=false
set SECRET_KEY=whatsapp-websocket-secret

echo.
echo 🚀 Iniciando servidor WebSocket WhatsApp Web
echo 📡 Host: %WS_HOST%
echo 🔌 Puerto: %WS_PORT%
echo 🐛 Debug: %DEBUG%
echo.

REM Verificar que Python está disponible
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python no está instalado
    pause
    exit /b 1
)

REM Verificar dependencias
python -c "import flask_socketio" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Flask-SocketIO no está instalado
    echo 💡 Ejecuta: pip install flask-socketio
    pause
    exit /b 1
)

REM Ejecutar servidor
echo ✅ Iniciando servidor WebSocket...
python websocket_server.py

pause
