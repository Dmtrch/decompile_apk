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

# Установка Apktool
RUN wget https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool -O /usr/local/bin/apktool && \
    chmod +x /usr/local/bin/apktool && \
    wget https://github.com/iBotPeaches/Apktool/releases/download/v2.9.1/apktool_2.9.1.jar -O /usr/local/bin/apktool.jar

# Установка Gradle
RUN wget https://services.gradle.org/distributions/gradle-8.4-bin.zip && \
    unzip gradle-8.4-bin.zip -d /opt && \
    ln -s /opt/gradle-8.4/bin/gradle /usr/local/bin/gradle && \
    rm gradle-8.4-bin.zip

# Установка Android SDK
ENV ANDROID_HOME /opt/android-sdk
RUN mkdir -p ${ANDROID_HOME}/cmdline-tools && \
    wget https://dl.google.com/android/repository/commandlinetools-linux-10406996_latest.zip && \
    unzip commandlinetools-linux-10406996_latest.zip -d ${ANDROID_HOME}/cmdline-tools && \
    mv ${ANDROID_HOME}/cmdline-tools/cmdline-tools ${ANDROID_HOME}/cmdline-tools/latest && \
    rm commandlinetools-linux-10406996_latest.zip

ENV PATH ${PATH}:${ANDROID_HOME}/cmdline-tools/latest/bin:${ANDROID_HOME}/platform-tools

# Принятие лицензий и установка необходимых компонентов
RUN yes | sdkmanager --licenses && \
    sdkmanager "platform-tools" "platforms;android-33" "build-tools;33.0.0"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Команда запуска будет переопределена в docker-compose для разных типов воркеров
CMD ["celery", "-A", "shared.celery_app", "worker", "--loglevel=info"]
