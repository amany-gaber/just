# main .py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from routes import router
import uvicorn
from config import settings
from schemas import ExceptionHandler

app = FastAPI()

# Enable CORSd
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the routes from routes.py
app.include_router(router)

@app.get("/")
def root():
    return {"message": "Click /docs to see the API documentation"}

@app.exception_handler(404)
def not_found_error(request, exc):
    return {"detail": "Page Not Found. Click /docs to see the API documentation"}

@app.exception_handler(Exception)
def handle_exception(request, exc):
    return {"message": f"Oops! {str(exc)}. Please try again!"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.DOMAIN,
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG_MODE,
    )



# user.py
from fastapi import APIRouter, File, UploadFile, HTTPException
import numpy as np
from services import EmotionInference

router = APIRouter(
    prefix="/CV_Specific_Job",
    tags=["predict"]
)

model_inference = EmotionInference()

@router.post("/inference")
async def inference(file: UploadFile = File(...)):
    file_extension = file.filename.split(".")[-1].lower()
    supported_formats = ["wav", "mp3", "ogg", "opus"]

    if file_extension not in supported_formats:
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload WAV, MP3, OGG, or OPUS.")

    try:
        audio_bytes = await file.read()

        result = model_inference.run_inference(audio_bytes, file_extension)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")



# service/main.py
import numpy as np
import onnxruntime as ort
import soundfile as sf
import io
from pydub import AudioSegment
import os
import subprocess
import tempfile

class EmotionInference:
    def __init__(self):
        model_dir = os.path.join(os.path.dirname(__file__), "..", "static")
        self.model_path = os.path.join(model_dir, "wav2vec2_emotion.onnx")
        self.session = self._load_model()
        self.id2label = {0: "calm", 1: "neutral", 2: "anxiety", 3: "confidence"}

    def _load_model(self):
        if os.path.exists(self.model_path):
            return ort.InferenceSession(self.model_path)
        else:
            raise FileNotFoundError(f"Model file not found at {self.model_path}")

    def convert_opus_to_wav_with_ffmpeg(self, audio_bytes):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".opus") as temp_in:
            temp_in.write(audio_bytes)
            temp_in_path = temp_in.name

        temp_out_path = temp_in_path.replace(".opus", ".wav")

        try:
            result = subprocess.run(
                ["ffmpeg", "-y", "-f", "ogg", "-c:a", "libopus", "-i", temp_in_path, temp_out_path],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print(f"FFmpeg stdout: {result.stdout}")
            print(f"FFmpeg stderr: {result.stderr}")

            with open(temp_out_path, "rb") as f:
                wav_data = f.read()

            return wav_data

        except subprocess.CalledProcessError as e:
            raise Exception(f"Error converting audio to WAV: {e.stderr}")
        finally:
            if os.path.exists(temp_in_path):
                os.remove(temp_in_path)
            if os.path.exists(temp_out_path):
                os.remove(temp_out_path)

    def convert_audio_to_wav(self, audio_bytes, format):
        audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format=format)
        wav_io = io.BytesIO()
        audio.export(wav_io, format="wav")
        return wav_io.getvalue()

    def preprocess_audio(self, audio_bytes, file_extension):
        if file_extension in ["mp3", "ogg", "opus"]:
            if file_extension == "opus":
                audio_bytes = self.convert_opus_to_wav_with_ffmpeg(audio_bytes)
            else:
                audio_bytes = self.convert_audio_to_wav(audio_bytes, file_extension)

        audio, samplerate = sf.read(io.BytesIO(audio_bytes))

        if len(audio.shape) > 1:
            audio = np.mean(audio, axis=1)

        input_tensor = np.expand_dims(audio, axis=0).astype(np.float32)
        return input_tensor

    def softmax(self, logits):
        exp_logits = np.exp(logits - np.max(logits))
        return exp_logits / np.sum(exp_logits)

    def run_inference(self, audio_bytes, file_extension):
        input_tensor = self.preprocess_audio(audio_bytes, file_extension)
        inputs = {self.session.get_inputs()[0].name: input_tensor}
        outputs = self.session.run(None, inputs)

        predicted_logits = outputs[0][0]
        probabilities = self.softmax(predicted_logits)

        sorted_indices = np.argsort(probabilities)[::-1]

        top_emotion_index = sorted_indices[0]
        top_emotion_label = self.id2label[top_emotion_index]
        top_emotion_confidence = f"{round(probabilities[top_emotion_index] * 100)}%"

        alternatives = {
            self.id2label[i]: f"{round(probabilities[i] * 100)}%"
            for i in sorted_indices[1:]
        }

        return {
            "emotion": top_emotion_label,
            "confidence": top_emotion_confidence,
            "alternatives": alternatives
        }


# docker compose file
services:
  api:
    image: cv-specific-job:1.0.0
    ports:
     - "${BACKEND_PORT:-8080}:8080"
    container_name: voice_toon_api
    restart: always
    env_file:
      - .env



# docker file
FROM ubuntu:20.04 AS builder-image
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.9 python3.9-dev python3.9-venv python3-pip python3-wheel \
    build-essential git \
    ffmpeg libavcodec-extra libopus0
RUN python3.9 -m venv /home/docker/venv
ENV PATH="/home/docker/venv/bin:$PATH"
RUN python3.9 -m pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM ubuntu:20.04 AS runner-image
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.9 python3-venv \
    ffmpeg libavcodec-extra libopus0
RUN useradd --create-home docker
COPY --from=builder-image /home/docker/venv /home/docker/venv
USER docker
RUN mkdir /home/docker/app
WORKDIR /home/docker/app
COPY ./src /home/docker/app
EXPOSE 8080
ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/home/docker/venv
ENV PATH="/home/docker/venv/bin:$PATH"
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "3", "--log-level", "debug", "--timeout-keep-alive", "1000"]


# main file 
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from routes import router
import uvicorn
from config import settings
from schemas import ExceptionHandler

app = FastAPI()

# Enable CORSd
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the routes from routes.py
app.include_router(router)

@app.get("/")
def root():
    return {"message": "Click /docs to see the API documentation"}

@app.exception_handler(404)
def not_found_error(request, exc):
    return {"detail": "Page Not Found. Click /docs to see the API documentation"}

@app.exception_handler(Exception)
def handle_exception(request, exc):
    return {"message": f"Oops! {str(exc)}. Please try again!"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.DOMAIN,
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG_MODE,
    )









# service.py
import uvicorn
from fastapi import APIRouter
from services import *

service = APIRouter(
    prefix="/CV_Specific_Job",
    tags=["Perdict"]
)


if __name__ == "__main__":
    uvicorn.run(service)

# uvicorn main:app --reload
