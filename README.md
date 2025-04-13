# just
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

    def _load_model(self):
        """
        Load the ONNX model.
        """
        if os.path.exists(self.model_path):
            return ort.InferenceSession(self.model_path)
        else:
            raise FileNotFoundError(f"Model file not found at {self.model_path}")

    def convert_audio_to_wav(self, audio_bytes, format):
        """
        Convert MP3/OGG to WAV if needed.
        """
        audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format=format)
        wav_io = io.BytesIO()
        audio.export(wav_io, format="wav")
        return wav_io.getvalue()

    def preprocess_audio(self, audio_bytes, file_extension):
        """
        Preprocess the audio file by converting to mono and preparing for model input.
        """
        if file_extension in ["mp3", "ogg"]:
            audio_bytes = self.convert_audio_to_wav(audio_bytes, file_extension)

        audio, samplerate = sf.read(io.BytesIO(audio_bytes))
        
        if len(audio.shape) > 1:
            audio = np.mean(audio, axis=1)  # Convert stereo to mono
        
        input_tensor = np.expand_dims(audio, axis=0).astype(np.float32)
        return input_tensor

    def softmax(self, logits):
        """
        Softmax function to convert logits to probabilities.
        """
        exp_logits = np.exp(logits - np.max(logits))  
        return exp_logits / np.sum(exp_logits)

    def run_inference(self, audio_bytes, file_extension):
        """
        Run inference on the given audio file.
        """
        input_tensor = self.preprocess_audio(audio_bytes, file_extension)
        inputs = {self.session.get_inputs()[0].name: input_tensor}
        outputs = self.session.run(None, inputs)
        
        predicted_logits = outputs[0][0]
        probabilities = self.softmax(predicted_logits)

        top_2_indices = np.argsort(probabilities)[-2:][::-1]
        top_2_emotions = {self.id2label[i]: f"{round(probabilities[i] * 100)}%" for i in top_2_indices}

        return top_2_emotions


def main():
    # Example usage
    model_inference = EmotionInference()

    # Load the audio file (this is just an example, replace with actual audio loading)
    with open("./services/audio_file.wav", "rb") as audio_file:
        audio_bytes = audio_file.read()
    
    file_extension = "wav"  # Set the file extension manually if needed (e.g., wav, mp3, ogg)
    
    top_2_emotions = model_inference.run_inference(audio_bytes, file_extension)
    
    # Print the result
    print(f"Top 2 emotions: {top_2_emotions}")

if __name__ == "__main__":


    # Load the audio file
    with open("How_Tone.wav", "rb") as audio_file:
        audio_bytes = audio_file.read()

    # Initialize the EmotionInference class
    model_inference = EmotionInference()

    top_2_emotions = model_inference.run_inference(audio_bytes, file_extension="wav")
    

    # Print the results
    print(f"Inference time: {inference_time:.2f} seconds")
    print(f"Top 2 emotions: {top_2_emotions}")

