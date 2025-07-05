#!/bin/bash

# Buildpack para instalar Chrome en Railway

set -e

echo "🔧 Instalando Chrome en Railway..."

# Actualizar lista de paquetes
apt-get update

# Instalar dependencias necesarias
apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    apt-transport-https \
    software-properties-common

# Agregar clave GPG de Google
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -

# Agregar repositorio de Chrome
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | tee /etc/apt/sources.list.d/google-chrome.list

# Actualizar lista de paquetes
apt-get update

# Instalar Google Chrome
apt-get install -y google-chrome-stable

# Verificar instalación
google-chrome --version

echo "✅ Chrome instalado exitosamente"

# Instalar ChromeDriver
CHROMEDRIVER_VERSION=$(google-chrome --version | sed -r 's/.*Chrome ([0-9]+\.[0-9]+\.[0-9]+).*/\1/' | sed 's/\.[0-9]*$//')
echo "🔧 Instalando ChromeDriver versión: $CHROMEDRIVER_VERSION"

wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROMEDRIVER_VERSION/chromedriver_linux64.zip
unzip /tmp/chromedriver.zip -d /tmp/
mv /tmp/chromedriver /usr/local/bin/chromedriver
chmod +x /usr/local/bin/chromedriver

# Verificar ChromeDriver
chromedriver --version

echo "✅ ChromeDriver instalado exitosamente"
