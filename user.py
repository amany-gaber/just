from fastapi import APIRouter, File, UploadFile, HTTPException
from io import BytesIO
import numpy as np
import onnxruntime as ort
import soundfile as sf
from pydub import AudioSegment
from services import EmotionInference


router = APIRouter(
    prefix="/voice",
    tags=["prdict"]
)

model_inference = EmotionInference()

@router.post("/inference")
async def inference(file: UploadFile = File(...)):
    file_extension = file.filename.split(".")[-1].lower()
    supported_formats = ["wav", "mp3", "ogg"]

    if file_extension not in supported_formats:
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload WAV, MP3, or OGG.")

    try:
        audio_bytes = await file.read()
        
        
        input_tensor = model_inference.preprocess_audio(audio_bytes, file_extension)

        inputs = {model_inference.session.get_inputs()[0].name: input_tensor}
        outputs = model_inference.session.run(None, inputs)
        
        predicted_logits = outputs[0][0]
        probabilities = model_inference.softmax(predicted_logits)

        top_2_indices = np.argsort(probabilities)[-2:][::-1]  
        top_2_emotions = {model_inference.id2label[i]: f"{round(probabilities[i] * 100)}%" for i in top_2_indices}

        response = {
            "top_emotions": top_2_emotions
        }

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
