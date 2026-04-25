import subprocess
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DecompilerService:
    def __init__(self, output_base_dir="/data/decompiled"):
        self.output_base_dir = output_base_dir
        os.makedirs(self.output_base_dir, exist_ok=True)

    def decompile(self, apk_path: str, job_id: str):
        project_dir = os.path.join(self.output_base_dir, job_id)
        os.makedirs(project_dir, exist_ok=True)
        
        results = {
            "apktool": self._run_apktool(apk_path, project_dir),
            "jadx": self._run_jadx(apk_path, project_dir)
        }
        
        return project_dir, results

    def _run_apktool(self, apk_path: str, output_dir: str):
        """Извлечение ресурсов и манифеста"""
        apktool_out = os.path.join(output_dir, "resources")
        try:
            logger.info(f"Running apktool on {apk_path}...")
            subprocess.run(
                ["apktool", "d", apk_path, "-o", apktool_out, "-f"],
                check=True, capture_output=True, text=True
            )
            return "success"
        except subprocess.CalledProcessError as e:
            logger.error(f"Apktool failed: {e.stderr}")
            return f"error: {e.stderr}"

    def _run_jadx(self, apk_path: str, output_dir: str):
        """Декомпиляция кода в Java"""
        jadx_out = os.path.join(output_dir, "sources")
        try:
            logger.info(f"Running jadx on {apk_path}...")
            subprocess.run(
                ["jadx", "-d", jadx_out, apk_path],
                check=True, capture_output=True, text=True
            )
            return "success"
        except subprocess.CalledProcessError as e:
            logger.error(f"Jadx failed: {e.stderr}")
            return f"error: {e.stderr}"
