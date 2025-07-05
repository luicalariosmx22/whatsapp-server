# Dockerfile para Railway con Chrome - Versión Ultra Simplificada
FROM python:3.11-slim

# Instalar dependencias básicas
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    xvfb \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Instalar Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | tee /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Instalar ChromeDriver usando versión fija compatible
RUN wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip" \
    && unzip /tmp/chromedriver.zip -d /tmp/ \
    && mv /tmp/chromedriver /usr/local/bin/chromedriver \
    && chmod +x /usr/local/bin/chromedriver \
    && rm /tmp/chromedriver.zip

# Verificar instalación
RUN google-chrome --version && chromedriver --version

# Configurar directorio de trabajo
WORKDIR /app

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV WS_HOST=0.0.0.0
ENV DEBUG=False
ENV RAILWAY_ENVIRONMENT=1
ENV DISPLAY=:99

# Puerto
EXPOSE 8080

# Comando de inicio
CMD ["python", "start_railway.py"]
