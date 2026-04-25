from shared.celery_app import app
from decompiler.service import DecompilerService
from decompiler.builder import BuilderService
from celery import chain
import logging

logger = logging.getLogger(__name__)
decompiler = DecompilerService()
builder = BuilderService()

@app.task(name="decompiler.decompile_apk")
def decompile_apk(apk_path: str, job_id: str):
    logger.info(f"Starting decompilation for job {job_id}, file: {apk_path}")
    
    try:
        project_dir, results = decompiler.decompile(apk_path, job_id)
        
        # Подготовка к сборке
        builder.prepare_gradle_project(project_dir)
        build_status, build_result = builder.build_apk(project_dir)
        
        # Формируем промежуточный результат для передачи в сканер
        decompile_results = {
            "decompilation": results,
            "build_back": {
                "status": build_status,
                "result": build_result
            },
            "project_dir": project_dir
        }
        
        # Запускаем задачу сканирования сразу после декомпиляции
        # Используем Celery chain для последовательного выполнения
        return decompile_results
        
    except Exception as e:
        logger.error(f"Decompilation job {job_id} failed: {str(e)}")
        return {
            "status": "error",
            "job_id": job_id,
            "error": str(e)
        }
