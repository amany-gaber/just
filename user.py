yaz@gpu:~/STT/api/src$ uvicorn main:app --host 0.0.0.0 --port 6498
Traceback (most recent call last):
  File "/home/yaz/.local/bin/uvicorn", line 8, in <module>
    sys.exit(main())
             ^^^^^^
  File "/opt/anaconda3/lib/python3.12/site-packages/click/core.py", line 1157, in __call__
    return self.main(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/anaconda3/lib/python3.12/site-packages/click/core.py", line 1078, in main
    rv = self.invoke(ctx)
         ^^^^^^^^^^^^^^^^
  File "/opt/anaconda3/lib/python3.12/site-packages/click/core.py", line 1434, in invoke
    return ctx.invoke(self.callback, **ctx.params)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/anaconda3/lib/python3.12/site-packages/click/core.py", line 783, in invoke
    return __callback(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/yaz/.local/lib/python3.12/site-packages/uvicorn/main.py", line 412, in main
    run(
  File "/home/yaz/.local/lib/python3.12/site-packages/uvicorn/main.py", line 579, in run
    server.run()
  File "/home/yaz/.local/lib/python3.12/site-packages/uvicorn/server.py", line 66, in run
    return asyncio.run(self.serve(sockets=sockets))
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/anaconda3/lib/python3.12/asyncio/runners.py", line 194, in run
    return runner.run(main)
           ^^^^^^^^^^^^^^^^
  File "/opt/anaconda3/lib/python3.12/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/anaconda3/lib/python3.12/asyncio/base_events.py", line 687, in run_until_complete
    return future.result()
           ^^^^^^^^^^^^^^^
  File "/home/yaz/.local/lib/python3.12/site-packages/uvicorn/server.py", line 70, in serve
    await self._serve(sockets)
  File "/home/yaz/.local/lib/python3.12/site-packages/uvicorn/server.py", line 77, in _serve
    config.load()
  File "/home/yaz/.local/lib/python3.12/site-packages/uvicorn/config.py", line 435, in load
    self.loaded_app = import_from_string(self.app)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/yaz/.local/lib/python3.12/site-packages/uvicorn/importer.py", line 19, in import_from_string
    module = importlib.import_module(module_str)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/anaconda3/lib/python3.12/importlib/__init__.py", line 90, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 995, in exec_module
  File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
  File "/home/yaz/STT/api/src/main.py", line 3, in <module>
    from routes import router
  File "/home/yaz/STT/api/src/routes/__init__.py", line 1, in <module>
    from .user import router
  File "/home/yaz/STT/api/src/routes/user.py", line 10, in <module>
    model_inference = EmotionInference()
                      ^^^^^^^^^^^^^^^^^^
  File "/home/yaz/STT/api/src/services/main.py", line 14, in __init__
    self.session = self._load_model()
                   ^^^^^^^^^^^^^^^^^^
  File "/home/yaz/STT/api/src/services/main.py", line 21, in _load_model
    raise FileNotFoundError(f"Model file not found at {self.model_path}")
FileNotFoundError: Model file not found at /home/yaz/STT/api/src/services/../static/wav2vec2_emotion.onnx
yaz@gpu:~/STT/api/src$ 







































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
