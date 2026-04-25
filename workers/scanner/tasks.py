from shared.celery_app import app
from scanner.service import ScannerService
from scanner.dynamic_analyzer import DynamicAnalyzerService
import logging

logger = logging.getLogger(__name__)
scanner = ScannerService()
dynamic_analyzer = DynamicAnalyzerService()

@app.task(name="scanner.scan_code")
def scan_code(decompile_results: dict, job_id: str, package_name: str = "com.example.app"):
    logger.info(f"Starting security scan for job {job_id}")
    
    project_dir = decompile_results.get("project_dir")
    if not project_dir:
        return {"status": "error", "error": "No project_dir found in decompile results"}

    try:
        # 1. Статический анализ
        static_results = scanner.scan(project_dir)
        
        # 2. Динамический анализ в песочнице
        dynamic_results = dynamic_analyzer.analyze(package_name)
        
        return {
            "status": "success",
            "job_id": job_id,
            "decompilation": decompile_results.get("decompilation"),
            "build_back": decompile_results.get("build_back"),
            "static_results": static_results,
            "dynamic_results": dynamic_results
        }
    except Exception as e:
        logger.error(f"Scan failed for job {job_id}: {str(e)}")
        return {
            "status": "error",
            "job_id": job_id,
            "error": str(e)
        }
