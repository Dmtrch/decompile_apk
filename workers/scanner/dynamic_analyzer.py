import frida
import time
import logging
import os
import subprocess

logger = logging.getLogger(__name__)

class DynamicAnalyzerService:
    def __init__(self, scripts_dir="/app/scanner/scripts", emulator_host="android-emulator:5555"):
        self.scripts_dir = scripts_dir
        self.emulator_host = emulator_host
        os.makedirs(self.scripts_dir, exist_ok=True)
        self._connect_adb()

    def _connect_adb(self):
        """Подключается к эмулятору через ADB"""
        try:
            logger.info(f"Connecting to ADB at {self.emulator_host}...")
            subprocess.run(["adb", "connect", self.emulator_host], check=True, capture_output=True)
        except Exception as e:
            logger.warning(f"Failed to connect to ADB: {str(e)}")

    def analyze(self, apk_path: str, package_name: str, duration=30):
        """
        Устанавливает APK в эмулятор, запускает его и прикрепляет Frida.
        """
        findings = []
        try:
            # 1. Установка APK
            logger.info(f"Installing {apk_path} to emulator...")
            subprocess.run(["adb", "-s", self.emulator_host, "install", "-r", apk_path], check=True)
            
            # 2. Подключение Frida
            # Ожидаем, что frida-server уже запущен в образе budtmo/docker-android
            device = frida.get_device_manager().add_remote_device(self.emulator_host)
            
            logger.info(f"Spawning {package_name}...")
            pid = device.spawn([package_name])
            session = device.attach(pid)
            
            # 3. Загрузка скриптов
            script_content = self.generate_frida_tracer()
            # Добавляем наш anti-lockout скрипт
            if os.path.exists("/app/sandbox/anti_lockout.js"):
                with open("/app/sandbox/anti_lockout.js", "r") as f:
                    script_content += f.read()

            script = session.create_script(script_content)
            
            def on_message(message, data):
                if message['type'] == 'send':
                    logger.info(f"[Frida] {message['payload']}")
                    findings.append({
                        "type": "dynamic_event",
                        "event": message['payload']
                    })
                else:
                    logger.error(f"[Frida Error] {message}")

            script.on('message', on_message)
            script.load()
            
            device.resume(pid)
            
            # 4. Наблюдение
            time.sleep(duration)
            
            session.detach()
            logger.info(f"Analysis for {package_name} completed.")
            
            return findings
        except Exception as e:
            logger.error(f"Frida analysis failed: {str(e)}")
            return [{"type": "error", "message": f"Real DAST failed: {str(e)}"}]

    def generate_frida_tracer(self):
        """Генерирует скрипт для трассировки системных вызовов и API"""
        return """
        Java.perform(function () {
            // Трассировка сетевых вызовов
            var URL = Java.use('java.net.URL');
            URL.$init.overload('java.lang.String').implementation = function (url) {
                send('[Network] App tried to connect to: ' + url);
                return this.$init(url);
            };

            // Трассировка доступа к файлам
            var File = Java.use('java.io.File');
            File.$init.overload('java.lang.String').implementation = function (path) {
                if (path.includes('/data/user/0/')) {
                    send('[FileIO] Sensitive file access: ' + path);
                }
                return this.$init(path);
            };
        });
        """
