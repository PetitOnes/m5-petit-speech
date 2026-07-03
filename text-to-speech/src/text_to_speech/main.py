from fastapi import FastAPI
from text_to_speech.api.routes import router

app = FastAPI()
app.include_router(router)