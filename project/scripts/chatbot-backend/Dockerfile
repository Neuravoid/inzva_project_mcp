# npx'in sorunsuz çalışması için tam bir Node.js imajını temel alıyoruz.
FROM node:20

# Bu Node.js imajının içine Python ve gerekli paketleri kuruyoruz (venv + distutils)
RUN apt-get update && \
    apt-get install -y python3 python3-venv python3-distutils build-essential && \
    rm -rf /var/lib/apt/lists/*

# Python ortam değişkenlerini ayarla
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Virtual environment oluştur
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app

# Ana 'scripts' dizinindeki requirements.txt dosyasını kopyala
COPY ./requirements.txt ./requirements.txt

# Upgrade pip/setuptools/wheel inside venv and install requirements using venv pip
RUN python3 -m pip install --upgrade pip setuptools wheel && \
    $VIRTUAL_ENV/bin/pip install --no-cache-dir -r requirements.txt

# Uygulama kaynak kodunu kopyala
COPY ./src ./src
COPY ./chatbot-backend/ ./

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
