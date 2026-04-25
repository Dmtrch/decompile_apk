from fastapi import APIRouter, UploadFile, File, HTTPException
from celery.result import AsyncResult
from workers.shared.celery_app import app as celery_app
import os
import uuid
import shutil

router = APIRouter()

UPLOAD_DIR = "/data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_apk(file: UploadFile = File(...)):
    if not file.filename.endswith(".apk"):
        raise HTTPException(status_code=400, detail="Only APK files are allowed")
    
    job_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{job_id}.apk")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Запуск задачи декомпиляции
    task = celery_app.send_task(
        "decompiler.decompile_apk",
        args=[file_path, job_id],
        task_id=job_id
    )
    
    return {
        "job_id": job_id,
        "status": "queued",
        "task_id": task.id
    }

@router.get("/status/{job_id}")
async def get_status(job_id: str):
    res = AsyncResult(job_id, app=celery_app)
    return {
        "job_id": job_id,
        "state": res.state,
        "result": res.result if res.ready() else None
    }
