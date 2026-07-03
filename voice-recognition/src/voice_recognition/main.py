from fastapi import FastAPI

from voice_recognition.api.routes import router

app = FastAPI(title="voice_recognition", version="0.1.0")
app.include_router(router)