from fastapi import FastAPI, Request
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mock_server")

app = FastAPI(title="Sandbox Mock Server")

@app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def catch_all(request: Request, path_name: str):
    body = await request.body()
    logger.info(f"Intercepted request: {request.method} /{path_name}")
    logger.info(f"Headers: {dict(request.headers)}")
    if body:
        logger.info(f"Body: {body.decode('utf-8', errors='ignore')}")
    
    # Возвращаем универсальный успешный ответ для предотвращения закрытия приложения
    return {
        "status": "ok",
        "message": "Intercepted by Sandbox",
        "data": {}
    }
