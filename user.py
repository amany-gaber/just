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
