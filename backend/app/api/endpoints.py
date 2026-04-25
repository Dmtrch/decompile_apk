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

from app.infra.report_generator import ReportGenerator
from app.infra.ai_analyzer import AIAnalyzer
from pydantic import BaseModel

report_gen = ReportGenerator()
ai_analyzer = AIAnalyzer()

class AIExplainRequest(BaseModel):
    code_snippet: str
    issue_description: str

@router.post("/ai/explain")
async def explain_issue(req: AIExplainRequest):
    analysis = await ai_analyzer.explain_vulnerability(req.code_snippet, req.issue_description)
    return analysis

@router.get("/report/{job_id}")
async def get_report(job_id: str):
    res = AsyncResult(job_id, app=celery_app)
    if not res.ready():
        return {"status": "processing", "job_id": job_id}
    
    result = res.result
    # В реальном приложении здесь был бы вызов цепочки задач (Decompile -> Scan)
    # Для прототипа эмулируем агрегацию
    
    static_results = result.get("static_results", {})
    dynamic_results = result.get("dynamic_results", [])
    
    scorecard = report_gen.generate_scorecard(static_results, dynamic_results)
    return scorecard
