from shared.celery_app import app
from decompiler.service import DecompilerService
from decompiler.builder import BuilderService
import logging

logger = logging.getLogger(__name__)
decompiler = DecompilerService()
builder = BuilderService()

@app.task(name="decompiler.decompile_apk")
def decompile_apk(apk_path: str, job_id: str):
    logger.info(f"Starting decompilation for job {job_id}, file: {apk_path}")

    try:
        project_dir, results = decompiler.decompile(apk_path, job_id)

        # Пытаемся подготовить проект к сборке
        builder.prepare_gradle_project(project_dir)
        build_status, build_result = builder.build_apk(project_dir)

        final_results = {
            "decompilation": results,
            "build_back": {
                "status": build_status,
                "result": build_result
            }
        }
...

            return {
                "status": "partial_success",
                "job_id": job_id,
                "project_dir": project_dir,
                "details": results
            }
    except Exception as e:
        logger.error(f"Decompilation job {job_id} failed: {str(e)}")
        return {
            "status": "error",
            "job_id": job_id,
            "error": str(e)
        }
