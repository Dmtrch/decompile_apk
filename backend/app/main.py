from fastapi import FastAPI

app = FastAPI(title="Decompile & Audit APK API")

@app.get("/")
async def root():
    return {"message": "Welcome to Decompile & Audit APK API"}
