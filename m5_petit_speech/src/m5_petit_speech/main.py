from fastapi import FastAPI
from m5_petit_speech.api.routes import router

app = FastAPI()
app.include_router(router)