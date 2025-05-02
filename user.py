#main
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




# requirements
# FastAPI packages:
uvicorn
fastapi
pydantic
pydantic_settings
python-multipart

# Services packages:
faster-whisper==0.10.0
fastapi==0.110.0
uvicorn[standard]==0.29.0
pydub==0.25.1
soundfile==0.12.1
transformers==4.40.0
torch==2.1.0
torchaudio==2.1.0







# user
from fastapi import APIRouter, UploadFile, File, HTTPException
from services import TranscribeService

router = APIRouter(
    prefix="/speech_to_text",
    tags=["transcribe"]
)

transcriber = TranscribeService()

@router.post("/")
async def transcribe_audio(file: UploadFile = File(...)):
    file_extension = file.filename.split(".")[-1].lower()
    supported_formats = ["wav", "mp3", "ogg", "opus"]

    if file_extension not in supported_formats:
        raise HTTPException(status_code=400, detail="Unsupported audio format")

    try:
        audio_bytes = await file.read()
        return transcriber.transcribe_from_bytes(audio_bytes, file_extension)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during transcription: {str(e)}")






# services/main
import torch
import torchaudio
import os
from transformers import Wav2Vec2ForSequenceClassification, Wav2Vec2FeatureExtractor

class EmotionInference:
    def __init__(self):
        model_dir = "/home/yaz/STT/api/src/static/"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(model_dir)
        self.model = Wav2Vec2ForSequenceClassification.from_pretrained(model_dir)
        self.model.to(self.device)
        self.model.eval()

        self.id2label = self.model.config.id2label

    def preprocess_audio(self, audio_bytes):
        waveform, sr = torchaudio.load(audio_bytes)
        if sr != 16000:
            waveform = torchaudio.transforms.Resample(orig_freq=sr, new_freq=16000)(waveform)
        return waveform.squeeze()

    def run_inference(self, audio_bytes, file_extension):
        # Save audio to a temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as f:
            f.write(audio_bytes)
            tmp_path = f.name

        try:
            waveform = self.preprocess_audio(tmp_path)
            inputs = self.feature_extractor(waveform.numpy(), sampling_rate=16000, return_tensors="pt", padding=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                logits = self.model(**inputs).logits
                probs = torch.nn.functional.softmax(logits, dim=-1)[0]
                top = torch.argmax(probs).item()
                return {
                    "emotion": self.id2label[str(top)],
                    "confidence": f"{round(probs[top].item() * 100)}%",
                    "alternatives": {
                        self.id2label[str(i)]: f"{round(probs[i].item() * 100)}%"
                        for i in range(len(probs)) if i != top
                    }
                }
        finally:
            os.remove(tmp_path)
