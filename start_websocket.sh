#!/bin/bash
# Script para ejecutar el servidor WebSocket de WhatsApp Web

# Configuración
export WS_PORT=5001
export WS_HOST=0.0.0.0
export DEBUG=false
export SECRET_KEY="whatsapp-websocket-secret-$(date +%s)"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Iniciando servidor WebSocket WhatsApp Web${NC}"
echo -e "${YELLOW}📡 Host: ${WS_HOST}${NC}"
echo -e "${YELLOW}🔌 Puerto: ${WS_PORT}${NC}"
echo -e "${YELLOW}🐛 Debug: ${DEBUG}${NC}"

# Verificar que Python está disponible
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 no está instalado${NC}"
    exit 1
fi

# Verificar que las dependencias están instaladas
python3 -c "import flask_socketio" 2>/dev/null || {
    echo -e "${RED}❌ Flask-SocketIO no está instalado${NC}"
    echo -e "${YELLOW}💡 Ejecuta: pip install flask-socketio${NC}"
    exit 1
}

# Ejecutar servidor
echo -e "${GREEN}✅ Iniciando servidor WebSocket...${NC}"
python3 websocket_server.py
