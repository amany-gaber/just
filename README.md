import uvicorn
from fastapi import APIRouter
from services import *

service = APIRouter(
    prefix="/voice",
    tags=["Perdict"]
)


if __name__ == "__main__":
    uvicorn.run(service)

# uvicorn main:app --reload

















from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_ROOT: str = "/api/v0"
    APP_NAME: str = "voice"
    APP_DESCRIPTION: str = "voice-toon"
    DOMAIN: str = "0.0.0.0"
    BACKEND_PORT: int = 8080
    DEBUG_MODE: bool = True






# fastapi packages:
uvicorn
fastapi
pydantic
pydantic_settings
python-multipart
# websockets

# services packages:
ultralytics
pillow
numpy
onnxruntime-gpu
onnxruntime
numpy
pydub
soundfile
psutil
requests



