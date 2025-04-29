# services/main.py
import cv2
import numpy as np
import mediapipe as mp
import pandas as pd
import pickle
import os
from tempfile import NamedTemporaryFile

class BodyLanguageInference:
    def __init__(self, model_path="./static/body_language.pkl"):
        self.model = self._load_model(model_path)
        self.mp_holistic = mp.solutions.holistic

    def _load_model(self, model_path):
        """
        Load the trained model.
        """
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                return pickle.load(f)
        else:
            raise FileNotFoundError(f"Model file not found at {model_path}")

    def process_video(self, file_path):
        """
        Process the uploaded video file and predict body language.
        """
        cap = cv2.VideoCapture(file_path)
        results_list = []
        
        with self.mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image.flags.writeable = False  
                results = holistic.process(image)
                
                try:
                    pose = results.pose_landmarks.landmark
                    pose_row = list(np.array([[landmark.x, landmark.y, landmark.z, landmark.visibility] for landmark in pose]).flatten())
                    
                    face = results.face_landmarks.landmark
                    face_row = list(np.array([[landmark.x, landmark.y, landmark.z, landmark.visibility] for landmark in face]).flatten())
                    
                    row = pose_row + face_row
                    
                    X = pd.DataFrame([row])
                    body_language_class = self.model.predict(X)[0]
                    body_language_prob = self.model.predict_proba(X)[0]
                    
                    results_list.append({
                        "class": body_language_class,
                        "probability": round(body_language_prob[np.argmax(body_language_prob)], 2)
                    })
                except:
                    pass
        
        cap.release()
        os.remove(file_path)
        return results_list
    
    def save_temp_file(self, file_bytes):
        """
        Save uploaded file temporarily.
        """
        temp = NamedTemporaryFile(delete=False, suffix=".mp4")
        temp.write(file_bytes)
        temp.close()
        return temp.name


# Local testing of the model
def test_model_local(video_path):
    """
    Test the model with a local video file.
    """
    body_language_inference = BodyLanguageInference()

    # Test processing a video locally
    results = body_language_inference.process_video(video_path)
    print("Predicted body language results:")
    for result in results:
        print(f"Class: {result['class']}, Probability: {result['probability']}")

# If this script is run directly, test with a local video
if __name__ == "__main__":
    test_video_path = "./services/102.mp4"  # Replace with your video path
    test_model_local(test_video_path)
