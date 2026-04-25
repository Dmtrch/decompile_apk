from shared.celery_app import app
from scanner.service import ScannerService
import logging

logger = logging.getLogger(__name__)
scanner = ScannerService()

@app.task(name="scanner.scan_code")
def scan_code(project_dir: str, job_id: str):
    logger.info(f"Starting security scan for job {job_id} in {project_dir}")
    
    try:
        results = scanner.scan(project_dir)
        return {
            "status": "success",
            "job_id": job_id,
            "results": results
        }
    except Exception as e:
        logger.error(f"Scan failed for job {job_id}: {str(e)}")
        return {
            "status": "error",
            "job_id": job_id,
            "error": str(e)
        }
