FROM python:3.11-slim

# Установка Java (нужна для Jadx) и других системных утилит
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-jre \
    wget \
    unzip \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Установка Jadx
RUN wget https://github.com/skylot/jadx/releases/download/v1.4.7/jadx-1.4.7.zip && \
    mkdir /opt/jadx && unzip jadx-1.4.7.zip -d /opt/jadx && \
    ln -s /opt/jadx/bin/jadx /usr/local/bin/jadx && \
    rm jadx-1.4.7.zip

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Команда запуска будет переопределена в docker-compose для разных типов воркеров
CMD ["celery", "-A", "shared.celery_app", "worker", "--loglevel=info"]
