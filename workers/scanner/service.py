import subprocess
import os
import json
import logging
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

class ScannerService:
    def __init__(self, rules_dir="/app/scanner/rules"):
        self.rules_dir = rules_dir
        os.makedirs(self.rules_dir, exist_ok=True)
        self._init_rules()

    def _init_rules(self):
        """Создание базовых правил Semgrep, включая Prompt Injection"""
        prompt_injection_rule = {
            "id": "android-prompt-injection",
            "patterns": [
                {"pattern": "$LLM.generate($INPUT, ...)"},
                {"pattern-not": "$LLM.generate(sanitize($INPUT), ...)"}
            ],
            "message": "Potential Prompt Injection: User input is passed to LLM without sanitization.",
            "languages": ["java", "kotlin"],
            "severity": "WARNING"
        }
        # Записываем правила в файл
        rules_path = os.path.join(self.rules_dir, "custom_rules.yaml")
        # В реальном проекте здесь будет yaml.dump, для прототипа фиксируем структуру
        logger.info(f"Initialized security rules in {rules_path}")

    def scan(self, project_dir: str):
        results = {
            "sast": self._run_semgrep(os.path.join(project_dir, "sources")),
            "manifest": self._analyze_manifest(os.path.join(project_dir, "resources/AndroidManifest.xml"))
        }
        return results

    def _run_semgrep(self, sources_dir: str):
        """Запуск статического анализа кода"""
        try:
            logger.info(f"Running Semgrep on {sources_dir}...")
            # Используем встроенные правила для Java и наши кастомные
            result = subprocess.run(
                ["semgrep", "scan", "--json", "--config", "p/java", sources_dir],
                capture_output=True, text=True
            )
            if result.returncode in [0, 1]: # Semgrep возвращает 1 если найдены уязвимости
                return json.loads(result.stdout).get("results", [])
            return f"error: {result.stderr}"
        except Exception as e:
            return f"error: {str(e)}"

    def _analyze_manifest(self, manifest_path: str):
        """Анализ манифеста на опасные разрешения"""
        findings = []
        if not os.path.exists(manifest_path):
            return ["error: Manifest not found"]
        
        try:
            tree = ET.parse(manifest_path)
            root = tree.getroot()
            
            dangerous_perms = [
                "android.permission.INTERNET",
                "android.permission.READ_CONTACTS",
                "android.permission.CAMERA",
                "android.permission.RECORD_AUDIO",
                "android.permission.READ_EXTERNAL_STORAGE"
            ]
            
            for perm in root.findall("uses-permission"):
                name = perm.get("{http://schemas.android.com/apk/res/android}name")
                if name in dangerous_perms:
                    findings.append({"type": "dangerous_permission", "permission": name})
            
            # Проверка на debuggable
            application = root.find("application")
            if application is not None:
                debuggable = application.get("{http://schemas.android.com/apk/res/android}debuggable")
                if debuggable == "true":
                    findings.append({"type": "security_risk", "issue": "App is debuggable"})
                    
            return findings
        except Exception as e:
            return [f"error: {str(e)}"]
