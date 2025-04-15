(newnev) yaz@gpu:~/Voice-toon/api$ docker run -d -p 4444:8080 voice-api
07e331ff3cf0a3568aec4a7e94fd913659a76efeac641bb02a6ea83765634128
docker: Error response from daemon: failed to set up container networking: driver failed programming external connectivity on endpoint nifty_robinson (0ea010fa85533cb2e641700c6836efd5d8bb59b50918d2e94f06b14ca8cd12ef): Bind for 0.0.0.0:4444 failed: port is already allocated

Run 'docker run --help' for more information
(newnev) yaz@gpu:~/Voice-toon/api$ 



import numpy as np
import onnxruntime as ort
import soundfile as sf
import io
from pydub import AudioSegment
import os

class EmotionInference:
    def __init__(self):
        model_dir = "/home/docker/app/static"
        self.model_path = os.path.join(model_dir, "wav2vec2_emotion.onnx")
        self.session = self._load_model()
        self.id2label = {0: "calm", 1: "neutral", 2: "anxiety", 3: "confidence"}
        self.allowed_formats = ["wav", "mp3", "ogg", "opus", "m4a"]

    def _load_model(self):
        if os.path.exists(self.model_path):
            return ort.InferenceSession(self.model_path)
        else:
            raise FileNotFoundError(f"Model file not found at {self.model_path}")

    def convert_audio_to_wav(self, audio_bytes, format):
        try:
            audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format=format)
            wav_io = io.BytesIO()
            audio.export(wav_io, format="wav")
            return wav_io.getvalue()
        except Exception as e:
            raise ValueError(f"Error converting audio to WAV: {str(e)}")

    def preprocess_audio(self, audio_bytes, file_extension):
        if file_extension not in self.allowed_formats and file_extension != "wav":
            raise ValueError(f"Unsupported file format: {file_extension}")

        if file_extension in ["opus", "mp3"]:
            audio_bytes = self.convert_audio_to_wav(audio_bytes, file_extension)

        audio, samplerate = sf.read(io.BytesIO(audio_bytes))
        if len(audio.shape) > 1:
            audio = np.mean(audio, axis=1)  # Convert to mono

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

        top = int(np.argmax(probabilities))
        top_label = self.id2label[top]
        top_conf = round(probabilities[top] * 100)

        alt = {
            self.id2label[i]: f"{round(probabilities[i] * 100)}%"
            for i in np.argsort(probabilities)[::-1]
            if i != top
        }

        return {
            "emotion": top_label,
            "confidence": f"{top_conf}%",
            "top_emotions": alt 
        }



from fastapi import APIRouter, File, UploadFile, HTTPException
from io import BytesIO
import numpy as np
import onnxruntime as ort
import soundfile as sf
from pydub import AudioSegment
from services import EmotionInference

router = APIRouter(
    prefix="/voice",
    tags=["predict"]
)

model_inference = EmotionInference()

@router.post("/inference")
async def inference(file: UploadFile = File(...)):
    file_extension = file.filename.split(".")[-1].lower()
    supported_formats = ["wav", "mp3", "ogg", "opus"]

    if file_extension not in supported_formats:
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload WAV, MP3, or OGG.")

    try:
        audio_bytes = await file.read()
        result = model_inference.run_inference(audio_bytes, file_extension)
        
        response = {
            "top_emotions": result['alternatives'], 
            "emotion": result['emotion'],  
            "confidence": result['confidence']  
        }

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")




