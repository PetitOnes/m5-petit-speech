from fastapi import FastAPI

from m5_petit_voice_recognition.api.routes import router

app = FastAPI(title="m5_petit_voice_recognition", version="0.1.0")
app.include_router(router)