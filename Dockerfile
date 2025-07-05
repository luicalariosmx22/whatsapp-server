# Dockerfile para Railway con Chrome
FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    apt-transport-https \
    software-properties-common \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Instalar Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | tee /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Instalar ChromeDriver
RUN CHROMEDRIVER_VERSION=$(google-chrome --version | sed -r 's/.*Chrome ([0-9]+\.[0-9]+\.[0-9]+).*/\1/' | sed 's/\.[0-9]*$//') \
    && wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROMEDRIVER_VERSION/chromedriver_linux64.zip \
    && unzip /tmp/chromedriver.zip -d /tmp/ \
    && mv /tmp/chromedriver /usr/local/bin/chromedriver \
    && chmod +x /usr/local/bin/chromedriver \
    && rm /tmp/chromedriver.zip

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# Configurar variables de entorno
ENV PYTHONUNBUFFERED=1
ENV WS_HOST=0.0.0.0
ENV DEBUG=False
ENV RAILWAY_ENVIRONMENT=1
ENV DISPLAY=:99

# Exponer puerto
EXPOSE 8080

# Comando de inicio
CMD ["python", "start_railway.py"]
