docker compose file 
services:
     fastapi:
       build:
         context: .
         dockerfile: Dockerfile
       ports:
         - "2030:2030"
       environment:
         - MONGODB_URL=mongodb://mongodb:27017
         - CELERY_BROKER_URL=redis://redis:6379/0
         - CELERY_RESULT_BACKEND=redis://redis:6379/0
       depends_on:
         - mongodb
         - redis
       networks:
         - interview-network

     celery:
       build:
         context: .
         dockerfile: Dockerfile
       command: celery -A app.tasks worker --loglevel=info
       environment:
         - MONGODB_URL=mongodb://mongodb:27017
         - CELERY_BROKER_URL=redis://redis:6379/0
         - CELERY_RESULT_BACKEND=redis://redis:6379/0
       depends_on:
         - mongodb
         - redis
       networks:
         - interview-network

     mongodb:
       image: mongo:6.0
       ports:
         - "27017:27017"
       volumes:
         - mongodb_data:/data/db
       networks:
         - interview-network

     mongo-express:
       image: mongo-express:latest
       ports:
         - "8027:8081"
       environment:
         - ME_CONFIG_MONGODB_SERVER=mongodb
         - ME_CONFIG_MONGODB_PORT=27017
         - ME_CONFIG_BASICAUTH=false
       depends_on:
         - mongodb
       networks:
         - interview-network

     redis:
       image: redis:7.0
       networks:
         - interview-network

networks:
     interview-network:
       driver: bridge

volumes:
     mongodb_data:



yaz@gpu:~/interview-system$ ls
 app  'app copy'   docker-compose.yml   Dockerfile   README.md   requirements.txt
yaz@gpu:~/interview-system$ cd app
yaz@gpu:~/interview-system/app$ ls
config.py  __init__.py  main.py  models.py  __pycache__  requirements.txt  tasks.py
yaz@gpu:~/interview-system/app$ cd ..





config 
  import os

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")





main.py
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from typing import List , Optional, Union  
from app.models import Interview, Question
from app.tasks import process_question_audio
from .tasks import generate_avatar_video
from .tasks import process_cv_file
from app.config import MONGODB_URL
import requests

app = FastAPI(debug=True)

client = MongoClient(MONGODB_URL)
db = client["interview_db"]
interviews_collection = db["interviews"]

TOPIC_OPTIONS = {
    "machine learning": "machine_learning",
    "cyber security": "cybersecurity",
    "data engineering": "data_engineering",
    "devops": "devops"
}

class StartInterviewRequest(BaseModel):
    user_id: str
    topic: str
    subtopics: List[str]



@app.post("/interviews/start")
async def start_interview(
    user_id: str = Form(...),
    topic: str = Form(...),
    subtopics: str = Form(...)  # comma-separated string
):
    # 🔤 Validate topic
    topic_key = TOPIC_OPTIONS.get(topic.lower())
    if not topic_key:
        raise HTTPException(status_code=400, detail="Invalid topic")

    subtopics_list = [s.strip() for s in subtopics.split(",")]

    # 🧠 Ask LLM for first question
    llm_response = requests.post(
        "http://10.100.102.6:8906/start_interview",
        json={
            "topic": topic_key,
            "subtopics": subtopics_list,
            "num_questions": 10,
            "candidate_info": user_id
        }
    ).json()

    session_id = llm_response["session_id"]
    first_question_text = llm_response["first_question"]

    # 🗣️ Convert question to audio (TTS)
    try:
        tts_response = requests.post(
            "http://10.100.102.6:8906/tts",
            json={"text": first_question_text}
        )
        tts_response.raise_for_status()
        tts_data = tts_response.json()
        audio_url = tts_data["audio_url"]

        # Fetch audio file from the TTS response
        audio_file = requests.get(audio_url)
        audio_file.raise_for_status()
        audio_bytes = audio_file.content

        avatar_response = requests.post(
            "http://10.100.102.6:4063/sync",
            files={"audio": ("question.mp3", audio_bytes, "audio/mpeg")}
        )

        if avatar_response.status_code == 200:
            try:
                avatar_video_url = avatar_response.json().get("video_url")
            except Exception as json_err:
                avatar_video_url = f"error: failed to parse JSON from avatar: {str(json_err)}"
        else:
            avatar_video_url = f"error: avatar service returned {avatar_response.status_code}: {avatar_response.text}"


    except Exception as e:
        avatar_video_url = f"error: {str(e)}"

    # 🧱 Build first question
    question_0 = Question(
        question_id=0,
        question_text=first_question_text,
        status="pending",
        speech_text=None,
        llm_score={},
        voice_tone={},
        face_emotion={},
        avatar_video_url=avatar_video_url
    )

    # 🧾 Insert Interview
    interview = Interview(
        user_id=user_id,
        session_id=session_id,
        started_at=datetime.utcnow(),
        finished_at=None,
        questions=[question_0],
        final_report=None
    )

    interview_data = interview.model_dump()
    interview_data["questions"] = [q.model_dump() for q in interview.questions]
    interview_data["started_at"] = interview_data["started_at"].isoformat()
    if interview_data["finished_at"] is not None:
        interview_data["finished_at"] = interview_data["finished_at"].isoformat()

    result = interviews_collection.insert_one(interview_data)

    return {
        "message": "Interview started",
        "session_id": session_id,
        "interview_id": str(result.inserted_id),
        "first_question": first_question_text,
        "avatar_video_url": avatar_video_url
    }


@app.get("/interviews/{interview_id}/question/{question_id}/avatar")
def get_avatar_video(interview_id: str, question_id: int):
    interview = interviews_collection.find_one({"_id": ObjectId(interview_id)})
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    for q in interview.get("questions", []):
        if q.get("question_id") == question_id:
            return {"video_url": q.get("avatar_video_url", None)}

    raise HTTPException(status_code=404, detail="Question not found")


 # ✅ make sure this import exists

@app.post("/interviews/next_question")
async def submit_and_next(
    interview_id: str = Form(...),
    audio_file: UploadFile = File(...)
):
    # 🧠 Read audio file
    audio_bytes = await audio_file.read()

    # 📄 Fetch the interview
    interview = interviews_collection.find_one({"_id": ObjectId(interview_id)})
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    session_id = interview["session_id"]

    # 🧠 Request next question from LLM
    try:
        llm_resp = requests.post(
            "http://10.100.102.6:8906/next_question",
            json={"session_id": session_id, "answer": "placeholder"}
        )
        llm_data = llm_resp.json()
        new_question_text = llm_data.get("question", "")
        finished = llm_data.get("finished", False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")

    # 🔢 Calculate new question_id
    existing_qs = interview.get("questions", [])
    max_qid = max(q.get("question_id", -1) for q in existing_qs)
    next_qid = max_qid + 1

    # ➕ Insert new question into DB
    new_question = {
        "question_id": next_qid,
        "question_text": new_question_text,
        "status": "pending",
        "speech_text": None,
        "llm_score": {},
        "voice_tone": {},
        "face_emotion": {},
        "avatar_video_url": None
    }

    interviews_collection.update_one(
        {"_id": ObjectId(interview_id)},
        {"$push": {"questions": new_question}}
    )

    # 🧠 Trigger background tasks
    process_question_audio.delay(interview_id, max_qid, audio_bytes)
    generate_avatar_video.delay(interview_id, next_qid, new_question_text)

    # 🔁 Mark last question as processing
    interviews_collection.update_one(
        {"_id": ObjectId(interview_id), "questions.question_id": max_qid},
        {"$set": {"questions.$.status": "processing"}}
    )

    return {
        "message": "Next question generated and previous is processing.",
        "next_question_id": next_qid,
        "next_question_text": new_question_text,
        "interview_id": interview_id
    }


GEMINI_API_KEY = "AIzaSyAmU0SodyoQbMh_-A1e0A1Pm-h0_gM6RkA"
GEMINI_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

@app.post("/interviews/finish/{interview_id}")
async def finish_interview(interview_id: str):
    interview = interviews_collection.find_one({"_id": ObjectId(interview_id)})
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    # ✅ No status check — let it finish regardless of question state

    # 📊 Build structured prompt for Gemini
    full_prompt = [
    "You are an expert AI interviewer evaluator.",
    "Based on the following technical interview session, write a comprehensive final report addressed directly to the candidate using 'you' language.",
    "Each question includes: the question text, transcript of your answer, LLM feedback, voice tone analysis, and facial emotion detection.",
    "Assess your technical knowledge, communication, confidence, and emotional cues.",
    "Highlight both strengths and weaknesses clearly.",
    "Then recommend specific areas of improvement based on weak spots.",
    "Finally, list concrete resources to improve: suggest online courses (like Coursera, Udemy, edX), YouTube channels, or books.",
    "Make the tone professional, constructive, and encouraging.",
    "Return **only the report**. No extra explanations or instructions."
            ]


    for q in interview["questions"]:
        q_text = q.get("question_text", "N/A")
        answer = q.get("speech_text", "N/A")
        feedback = q.get("llm_score", {}).get("feedback", "No feedback available.")
        voice = q.get("voice_tone", {})
        face = q.get("face_emotion", {})

        voice_summary = f"Emotion: {voice.get('emotion', 'N/A')}, Confidence: {voice.get('confidence', 'N/A')}, Alternatives: {voice.get('alternatives', {})}"
        face_summary = ", ".join([
            f"{e['class']} ({e['percentage']}%)"
            for e in face.get("top_emotions", [])
        ]) if face.get("top_emotions") else "No emotion detected"

        full_prompt.append(
f"""
📌 **Question**: {q_text}
🗣️ **Transcript**: {answer}
🧠 **LLM Feedback**: {feedback}
🎤 **Voice Tone**: {voice_summary}
📸 **Facial Emotion**: {face_summary}
""")

    combined_prompt = "\n".join(full_prompt)

    # 🤖 Call Gemini
    try:
        gemini_payload = {
            "contents": [{
                "parts": [{"text": combined_prompt}]
            }]
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(GEMINI_ENDPOINT, json=gemini_payload, headers=headers)
        response.raise_for_status()

        gemini_data = response.json()
        summary_text = gemini_data["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        summary_text = f"❌ Gemini error: {str(e)}"

    # 📝 Save final report
    final_report = {
        "summary": summary_text,
        "overall_score": 8.5  # Optional: still static
    }

    interviews_collection.update_one(
        {"_id": ObjectId(interview_id)},
        {"$set": {
            "finished_at": datetime.utcnow(),
            "final_report": final_report
        }}
    )

    return {
        "message": "Interview finished and evaluated by Gemini.",
        "final_report": final_report
    }



@app.get("/interviews/id/by_user/{user_id}")
async def get_latest_interview_id(user_id: str):
    interview = interviews_collection.find_one(
        {"user_id": user_id},
        sort=[("started_at", -1)]
    )
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    return {"interview_id": str(interview["_id"])}



@app.post("/cv/analyze")
async def analyze_cv(user_id: str = Form(...), cv_file: UploadFile = File(...)):
    cv_bytes = await cv_file.read()
    process_cv_file.delay(user_id, cv_bytes, cv_file.filename)

    return {"message": "CV received and processing", "filename": cv_file.filename}


@app.get("/cv/by_user/{user_id}")
def get_cv_by_user(user_id: str):
    record = db["cv_analysis"].find_one({"user_id": user_id}, sort=[("created_at", -1)])
    if not record:
        raise HTTPException(status_code=404, detail="No CV record found.")
    
    record["_id"] = str(record["_id"])  # MongoDB ID fix
    return record



import app.tasks as t
print(">>> Tasks available:", dir(t))


from fastapi.responses import JSONResponse


@app.get("/interviews/all")
def get_all_interviews():
    interviews = list(interviews_collection.find())
    for interview in interviews:
        interview["_id"] = str(interview["_id"])
        if isinstance(interview.get("started_at"), datetime):
            interview["started_at"] = interview["started_at"].isoformat()
        if isinstance(interview.get("finished_at"), datetime):
            interview["finished_at"] = interview["finished_at"].isoformat()
    return JSONResponse(content=interviews)



@app.get("/debug/avatar")
def test_avatar_gen(interview_id: str, question_id: int, text: str):
    from app.tasks import generate_avatar_video
    generate_avatar_video.delay(interview_id, question_id, text)
    return {"msg": "triggered"}



models.py
    from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

class Question(BaseModel):
    question_id: int
    question_text: str
    status: str
    speech_text: Optional[str]
    llm_score: Dict
    voice_tone: Dict
    face_emotion: Dict
    avatar_video_url: Optional[str] = None


class Interview(BaseModel):
    user_id: str
    session_id: Optional[str] = None
    started_at: datetime
    finished_at: Optional[datetime]
    questions: List[Question]
    final_report: Optional[Dict]

class CVMatch(BaseModel):
    job_title: str
    governorate: str
    professional_level: str
    similarity_percentage: float
    matched_skills: List[str]
    missing_skills: List[str]
    pie_chart_data: Dict[str, float]

class CVAnalysisResult(BaseModel):
    user_id: str
    cv_filename: str
    cv_skills: List[str]
    top_matches: List[CVMatch]
    bar_chart_data: Dict[str, List]
    created_at: datetime




requirements
               fastapi==0.115.0
uvicorn==0.30.6
pymongo==4.8.0
celery==5.4.0
redis==5.0.8
pydantic==2.9.2
requests==2.31.0
python-multipart==0.0.12
requests


tasks
  import requests
from celery import Celery
from pymongo import MongoClient
from bson import ObjectId
from app.config import MONGODB_URL, CELERY_BROKER_URL, CELERY_RESULT_BACKEND
import io
from datetime import datetime


celery = Celery(
    "tasks",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)

@celery.task
def process_question_audio(interview_id: str, question_id: int, audio_bytes: bytes, filename: str = "audio"):
    client = MongoClient(MONGODB_URL)
    db = client["interview_db"]
    interviews_collection = db["interviews"]

    try:
        # 🔍 Detect extension if any
        extension = filename.split('.')[-1] if '.' in filename else 'wav'
        file_stream = io.BytesIO(audio_bytes)
        file_stream.name = f"audio.{extension}"

        # 1️⃣ TRANSCRIBE AUDIO
        stt_response = requests.post(
            "http://10.100.102.6:4004/audio/upload_and_transcribe",
            files={"file": file_stream}
        )
        stt_data = stt_response.json()
        transcript = stt_data.get("transcription", "")

        interviews_collection.update_one(
            {"_id": ObjectId(interview_id), "questions.question_id": question_id},
            {"$set": {"questions.$.speech_text": transcript}}
        )

    except Exception as e:
        transcript = ""
        interviews_collection.update_one(
            {"_id": ObjectId(interview_id), "questions.question_id": question_id},
            {"$set": {"questions.$.speech_text": f"STT error: {str(e)}"}}
        )

    try:
        # 2️⃣ VOICE EMOTION (reuse stream)
        file_stream.seek(0)
        voice_emotion_response = requests.post(
            "http://10.100.102.6:4444/voice/inference",
            files={"file": file_stream}
        )
        voice_emotion_data = voice_emotion_response.json()

        interviews_collection.update_one(
            {"_id": ObjectId(interview_id), "questions.question_id": question_id},
            {"$set": {"questions.$.voice_tone": voice_emotion_data}}
        )

    except Exception as e:
        interviews_collection.update_one(
            {"_id": ObjectId(interview_id), "questions.question_id": question_id},
            {"$set": {"questions.$.voice_tone": {"error": str(e)}}}
        )

    try:
        # 3️⃣ FEEDBACK
        interview = interviews_collection.find_one({"_id": ObjectId(interview_id)})
        session_id = interview.get("session_id")

        feedback_response = requests.post(
            "http://10.100.102.6:8906/feedback",
            json={"session_id": session_id}
        )
        feedback_data = feedback_response.json()

        interviews_collection.update_one(
            {"_id": ObjectId(interview_id), "questions.question_id": question_id},
            {"$set": {
                "questions.$.llm_score": feedback_data,
                "questions.$.status": "done"
            }}
        )

    except Exception as e:
        interviews_collection.update_one(
            {"_id": ObjectId(interview_id), "questions.question_id": question_id},
            {"$set": {
                "questions.$.llm_score": {"error": str(e)},
                "questions.$.status": "done"
            }}
        )

    client.close()

@celery.task
def generate_avatar_video(interview_id: str, question_id: int, question_text: str):
    import requests
    import io
    import logging
    from pymongo import MongoClient
    from bson import ObjectId

    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger(__name__)

    client = MongoClient(MONGODB_URL)
    db = client["interview_db"]
    interviews_collection = db["interviews"]

    video_url = "error: unknown"

    try:
        log.info(f"[🔊] Sending question to TTS: {question_text}")
        tts_resp = requests.post(
            "http://10.100.102.6:8906/tts",
            json={"text": question_text},
            headers={"accept": "audio/mpeg"},
            stream=True,
            timeout=15
        )

        if tts_resp.status_code != 200:
            raise Exception(f"TTS failed with status {tts_resp.status_code}: {tts_resp.text}")

        audio_stream = io.BytesIO(tts_resp.content)
        audio_stream.name = "output.mp3"
        log.info(f"[✅] Got audio from TTS ({len(tts_resp.content)} bytes)")

        log.info("[📤] Sending audio to avatar /sync endpoint")
        avatar_resp = requests.post(
            "http://10.100.102.6:4063/sync",
            files={"audio": ("output.mp3", audio_stream, "audio/mpeg")},
            headers={"accept": "application/json"},
            timeout=20
        )

        avatar_text = avatar_resp.text.strip()
        log.info(f"[🔍] Avatar raw response text: {avatar_text}")

        if avatar_resp.status_code != 200:
            raise Exception(f"Avatar sync failed: {avatar_resp.status_code} - {avatar_text}")

        try:
            avatar_data = avatar_resp.json()
            video_url = avatar_data.get("video_url", "error: no video_url")
        except Exception as json_err:
            video_url = f"error: could not parse avatar JSON: {json_err} | content: {avatar_text}"
            log.error(video_url)

    except Exception as e:
        video_url = f"error: {str(e)}"
        log.error(f"[❌] Avatar pipeline failed: {video_url}")

    # Save to DB
    result = interviews_collection.update_one(
        {"_id": ObjectId(interview_id), "questions.question_id": question_id},
        {"$set": {"questions.$.avatar_video_url": video_url}}
    )
    log.info(f"[💾] Avatar video URL saved to DB for qid={question_id} | modified={result.modified_count}")
    client.close()




@celery.task
def process_cv_file(user_id: str, file_bytes: bytes, filename: str):
    client = MongoClient(MONGODB_URL)
    db = client["interview_db"]
    collection = db["cv_analysis"]

    try:
        file_stream = io.BytesIO(file_bytes)
        file_stream.name = filename

        response = requests.post(
            "http://10.100.102.6:6438/cv/inference",
            files={"file": file_stream}
        )
        data = response.json()

        cv_record = {
            "user_id": user_id,
            "cv_filename": filename,
            "cv_skills": data.get("cv_skills", []),
            "top_matches": data.get("top_matches", []),
            "bar_chart_data": data.get("bar_chart_data", {}),
            "created_at": datetime.utcnow()
        }

        collection.insert_one(cv_record)

    except Exception as e:
        print(f"❌ Error processing CV: {e}")
    finally:
        client.close()






""" @celery.task
def process_question_video(interview_id: str, question_id: int, video_bytes: bytes):
    client = MongoClient(MONGODB_URL)
    db = client["interview_db"]
    interviews_collection = db["interviews"]

    try:
        file_stream = io.BytesIO(video_bytes)
        file_stream.name = "video.mp4"

        response = requests.post(
            "http://10.100.102.6:4400/video/inference",
            files={"file": file_stream}
        )
        face_emotion_data = response.json()

        interviews_collection.update_one(
            {"_id": ObjectId(interview_id), "questions.question_id": question_id},
            {"$set": {"questions.$.face_emotion": face_emotion_data}}
        )

    except Exception as e:
        interviews_collection.update_one(
            {"_id": ObjectId(interview_id), "questions.question_id": question_id},
            {"$set": {"questions.$.face_emotion": {"error": str(e)}}}
        )

    client.close() """





print(f"✅ Registered Celery tasks: {celery.tasks.keys()}")



















yaz@gpu:~/interview-system$ docker compose down
[+] Running 6/6
 ✔ Container interview-system-mongo-express-1  Removed                                                                                                  0.0s 
 ✔ Container interview-system-celery-1         Removed                                                                                                  0.0s 
 ✔ Container interview-system-fastapi-1        Removed                                                                                                  0.0s 
 ✔ Container interview-system-mongodb-1        Removed                                                                                                  0.0s 
 ✔ Container interview-system-redis-1          Removed                                                                                                  0.0s 
 ✔ Network interview-system_interview-network  Removed                                                                                                  0.2s 
yaz@gpu:~/interview-system$ docker compose up --build
Compose can now delegate builds to bake for better performance.
 To do so, set COMPOSE_BAKE=true.
[+] Building 1.5s (16/19)                                                                                                                     docker:default
 => [fastapi internal] load build definition from Dockerfile                                                                                            0.0s
 => => transferring dockerfile: 240B                                                                                                                    0.0s
 => [celery internal] load build definition from Dockerfile                                                                                             0.0s
 => => transferring dockerfile: 240B                                                                                                                    0.0s
 => [fastapi internal] load metadata for docker.io/library/python:3.11-slim                                                                             1.3s
 => [celery internal] load .dockerignore                                                                                                                0.0s
 => => transferring context: 2B                                                                                                                         0.0s
 => [fastapi internal] load .dockerignore                                                                                                               0.0s
 => => transferring context: 2B                                                                                                                         0.0s
 => [fastapi 1/5] FROM docker.io/library/python:3.11-slim@sha256:74132ced0002947303bc75654c7d51d3818435fe1c0ec6e4d84f7ca4d0849878                       0.0s
 => => resolve docker.io/library/python:3.11-slim@sha256:74132ced0002947303bc75654c7d51d3818435fe1c0ec6e4d84f7ca4d0849878                               0.0s
 => [celery internal] load build context                                                                                                                0.0s
 => => transferring context: 618B                                                                                                                       0.0s
 => [fastapi internal] load build context                                                                                                               0.0s
 => => transferring context: 618B                                                                                                                       0.0s
 => CACHED [celery 2/5] WORKDIR /app                                                                                                                    0.0s
 => CACHED [celery 3/5] COPY requirements.txt .                                                                                                         0.0s
 => CACHED [fastapi 4/5] RUN pip install --no-cache-dir -r requirements.txt                                                                             0.0s
 => [fastapi 5/5] COPY app/ ./app/                                                                                                                      0.0s
 => [fastapi] exporting to image                                                                                                                        0.0s
 => => exporting layers                                                                                                                                 0.0s
 => => writing image sha256:0adb08424e2d67d492f14e62d03e43713400a4f44b4a980459daaa75e109340e                                                            0.0s
 => => naming to docker.io/library/interview-system-fastapi                                                                                             0.0s
 => [celery] exporting to image                                                                                                                         0.0s
 => => exporting layers                                                                                                                                 0.0s
 => => writing image sha256:92b6841608254ad8f7006b02e151d551db1136cef2072fa09fe4b2e866baa289                                                            0.0s
 => => naming to docker.io/library/interview-system-celery                                                                                              0.0s
 => [celery] resolving provenance for metadata file                                                                                                     0.0s
 => [fastapi] resolving provenance for metadata file                                                                                                    0.0s
[+] Running 8/8
 ✔ celery                                      Built                                                                                                    0.0s 
 ✔ fastapi                                     Built                                                                                                    0.0s 
 ✔ Network interview-system_interview-network  Created                                                                                                  0.1s 
 ✔ Container interview-system-redis-1          Created                                                                                                  0.0s 
 ✔ Container interview-system-mongodb-1        Created                                                                                                  0.0s 
 ✔ Container interview-system-mongo-express-1  Created                                                                                                  0.0s 
 ✔ Container interview-system-fastapi-1        Created                                                                                                  0.0s 
 ✔ Container interview-system-celery-1         Created                                                                                                  0.0s 
Attaching to celery-1, fastapi-1, mongo-express-1, mongodb-1, redis-1
redis-1          | 1:C 11 Jun 2025 09:43:35.046 # oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
redis-1          | 1:C 11 Jun 2025 09:43:35.046 # Redis version=7.0.15, bits=64, commit=00000000, modified=0, pid=1, just started
redis-1          | 1:C 11 Jun 2025 09:43:35.046 # Warning: no config file specified, using the default config. In order to specify a config file use redis-server /path/to/redis.conf
redis-1          | 1:M 11 Jun 2025 09:43:35.047 * monotonic clock: POSIX clock_gettime
redis-1          | 1:M 11 Jun 2025 09:43:35.048 * Running mode=standalone, port=6379.
redis-1          | 1:M 11 Jun 2025 09:43:35.048 # Server initialized
redis-1          | 1:M 11 Jun 2025 09:43:35.048 # WARNING Memory overcommit must be enabled! Without it, a background save or replication may fail under low memory condition. Being disabled, it can can also cause failures without low memory condition, see https://github.com/jemalloc/jemalloc/issues/1328. To fix this issue add 'vm.overcommit_memory = 1' to /etc/sysctl.conf and then reboot or run the command 'sysctl vm.overcommit_memory=1' for this to take effect.
redis-1          | 1:M 11 Jun 2025 09:43:35.049 * Ready to accept connections
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:35.149+00:00"},"s":"I",  "c":"CONTROL",  "id":23285,   "ctx":"main","msg":"Automatically disabling TLS 1.0, to force-enable TLS 1.0 specify --sslDisabledProtocols 'none'"}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:35.150+00:00"},"s":"I",  "c":"NETWORK",  "id":4915701, "ctx":"main","msg":"Initialized wire specification","attr":{"spec":{"incomingExternalClient":{"minWireVersion":0,"maxWireVersion":17},"incomingInternalClient":{"minWireVersion":0,"maxWireVersion":17},"outgoing":{"minWireVersion":6,"maxWireVersion":17},"isInternalClient":true}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:35.150+00:00"},"s":"I",  "c":"NETWORK",  "id":4648601, "ctx":"main","msg":"Implicit TCP FastOpen unavailable. If TCP FastOpen is required, set tcpFastOpenServer, tcpFastOpenClient, and tcpFastOpenQueueSize."}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:35.151+00:00"},"s":"I",  "c":"REPL",     "id":5123008, "ctx":"main","msg":"Successfully registered PrimaryOnlyService","attr":{"service":"TenantMigrationDonorService","namespace":"config.tenantMigrationDonors"}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:35.151+00:00"},"s":"I",  "c":"REPL",     "id":5123008, "ctx":"main","msg":"Successfully registered PrimaryOnlyService","attr":{"service":"TenantMigrationRecipientService","namespace":"config.tenantMigrationRecipients"}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:35.151+00:00"},"s":"I",  "c":"REPL",     "id":5123008, "ctx":"main","msg":"Successfully registered PrimaryOnlyService","attr":{"service":"ShardSplitDonorService","namespace":"config.tenantSplitDonors"}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:35.151+00:00"},"s":"I",  "c":"CONTROL",  "id":5945603, "ctx":"main","msg":"Multi threading initialized"}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:35.151+00:00"},"s":"I",  "c":"CONTROL",  "id":4615611, "ctx":"initandlisten","msg":"MongoDB starting","attr":{"pid":1,"port":27017,"dbPath":"/data/db","architecture":"64-bit","host":"dc67d1ed3349"}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:35.151+00:00"},"s":"I",  "c":"CONTROL",  "id":23403,   "ctx":"initandlisten","msg":"Build Info","attr":{"buildInfo":{"version":"6.0.22","gitVersion":"ee527360b84c6798535ee0895de3c7186b3522f9","openSSLVersion":"OpenSSL 3.0.2 15 Mar 2022","modules":[],"allocator":"tcmalloc","environment":{"distmod":"ubuntu2204","distarch":"x86_64","target_arch":"x86_64"}}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:35.151+00:00"},"s":"I",  "c":"CONTROL",  "id":51765,   "ctx":"initandlisten","msg":"Operating System","attr":{"os":{"name":"Ubuntu","version":"22.04"}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:35.151+00:00"},"s":"I",  "c":"CONTROL",  "id":21951,   "ctx":"initandlisten","msg":"Options set by command line","attr":{"options":{"net":{"bindIp":"*"}}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:35.153+00:00"},"s":"I",  "c":"STORAGE",  "id":22270,   "ctx":"initandlisten","msg":"Storage engine to use detected by data files","attr":{"dbpath":"/data/db","storageEngine":"wiredTiger"}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:35.153+00:00"},"s":"I",  "c":"STORAGE",  "id":22297,   "ctx":"initandlisten","msg":"Using the XFS filesystem is strongly recommended with the WiredTiger storage engine. See http://dochub.mongodb.org/core/prodnotes-filesystem","tags":["startupWarnings"]}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:35.153+00:00"},"s":"I",  "c":"STORAGE",  "id":22315,   "ctx":"initandlisten","msg":"Opening WiredTiger","attr":{"config":"create,cache_size=63752M,session_max=33000,eviction=(threads_min=4,threads_max=4),config_base=false,statistics=(fast),log=(enabled=true,remove=true,path=journal,compressor=snappy),builtin_extension_config=(zstd=(compression_level=6)),file_manager=(close_idle_time=600,close_scan_interval=10,close_handle_minimum=2000),statistics_log=(wait=0),json_output=(error,message),verbose=[recovery_progress:1,checkpoint_progress:1,compact_progress:1,backup:0,checkpoint:0,compact:0,evict:0,history_store:0,recovery:0,rts:0,salvage:0,tiered:0,timestamp:0,transaction:0,verify:0,log:0],"}}
celery-1         | Usage: celery [OPTIONS] COMMAND [ARGS]...
celery-1         | Try 'celery --help' for help.
celery-1         | 
celery-1         | Error: Invalid value for '-A' / '--app': 
celery-1         | Unable to load celery application.
celery-1         | While trying to load the module app.tasks.celery the following error occurred:
celery-1         | Traceback (most recent call last):
celery-1         |   File "/usr/local/lib/python3.11/site-packages/celery/bin/celery.py", line 58, in convert
celery-1         |     return find_app(value)
celery-1         |            ^^^^^^^^^^^^^^^
celery-1         |   File "/usr/local/lib/python3.11/site-packages/celery/app/utils.py", line 383, in find_app
celery-1         |     sym = symbol_by_name(app, imp=imp)
celery-1         |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
celery-1         |   File "/usr/local/lib/python3.11/site-packages/kombu/utils/imports.py", line 59, in symbol_by_name
celery-1         |     module = imp(module_name, package=package, **kwargs)
celery-1         |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
celery-1         |   File "/usr/local/lib/python3.11/site-packages/celery/utils/imports.py", line 109, in import_from_cwd
celery-1         |     return imp(module, package=package)
celery-1         |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
celery-1         |   File "/usr/local/lib/python3.11/importlib/__init__.py", line 126, in import_module
celery-1         |     return _bootstrap._gcd_import(name[level:], package, level)
celery-1         |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
celery-1         |   File "<frozen importlib._bootstrap>", line 1204, in _gcd_import
celery-1         |   File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
celery-1         |   File "<frozen importlib._bootstrap>", line 1147, in _find_and_load_unlocked
celery-1         |   File "<frozen importlib._bootstrap>", line 690, in _load_unlocked
celery-1         |   File "<frozen importlib._bootstrap_external>", line 940, in exec_module
celery-1         |   File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
celery-1         |   File "/app/app/tasks.py", line 1, in <module>
celery-1         |     import requests
celery-1         | ModuleNotFoundError: No module named 'requests'
celery-1         | 
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:35.639+00:00"},"s":"I",  "c":"WTRECOV",  "id":22430,   "ctx":"initandlisten","msg":"WiredTiger message","attr":{"message":{"ts_sec":1749635015,"ts_usec":639760,"thread":"1:0x7b6ac8909cc0","session_name":"txn-recover","category":"WT_VERB_RECOVERY_PROGRESS","category_id":30,"verbose_level":"DEBUG","verbose_level_id":1,"msg":"Recovering log 10 through 11"}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:35.698+00:00"},"s":"I",  "c":"WTRECOV",  "id":22430,   "ctx":"initandlisten","msg":"WiredTiger message","attr":{"message":{"ts_sec":1749635015,"ts_usec":698720,"thread":"1:0x7b6ac8909cc0","session_name":"txn-recover","category":"WT_VERB_RECOVERY_PROGRESS","category_id":30,"verbose_level":"DEBUG","verbose_level_id":1,"msg":"Recovering log 11 through 11"}}}
celery-1 exited with code 2
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:35.799+00:00"},"s":"I",  "c":"WTRECOV",  "id":22430,   "ctx":"initandlisten","msg":"WiredTiger message","attr":{"message":{"ts_sec":1749635015,"ts_usec":799364,"thread":"1:0x7b6ac8909cc0","session_name":"txn-recover","category":"WT_VERB_RECOVERY_PROGRESS","category_id":30,"verbose_level":"DEBUG","verbose_level_id":1,"msg":"Main recovery loop: starting at 10/10880 to 11/256"}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:35.924+00:00"},"s":"I",  "c":"WTRECOV",  "id":22430,   "ctx":"initandlisten","msg":"WiredTiger message","attr":{"message":{"ts_sec":1749635015,"ts_usec":924243,"thread":"1:0x7b6ac8909cc0","session_name":"txn-recover","category":"WT_VERB_RECOVERY_PROGRESS","category_id":30,"verbose_level":"DEBUG","verbose_level_id":1,"msg":"Recovering log 10 through 11"}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:36.010+00:00"},"s":"I",  "c":"WTRECOV",  "id":22430,   "ctx":"initandlisten","msg":"WiredTiger message","attr":{"message":{"ts_sec":1749635016,"ts_usec":10025,"thread":"1:0x7b6ac8909cc0","session_name":"txn-recover","category":"WT_VERB_RECOVERY_PROGRESS","category_id":30,"verbose_level":"DEBUG","verbose_level_id":1,"msg":"Recovering log 11 through 11"}}}
fastapi-1        | Traceback (most recent call last):
fastapi-1        |   File "/usr/local/bin/uvicorn", line 8, in <module>
fastapi-1        |     sys.exit(main())
fastapi-1        |              ^^^^^^
fastapi-1        |   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1442, in __call__
fastapi-1        |     return self.main(*args, **kwargs)
fastapi-1        |            ^^^^^^^^^^^^^^^^^^^^^^^^^^
fastapi-1        |   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1363, in main
fastapi-1        |     rv = self.invoke(ctx)
fastapi-1        |          ^^^^^^^^^^^^^^^^
fastapi-1        |   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1226, in invoke
fastapi-1        |     return ctx.invoke(self.callback, **ctx.params)
fastapi-1        |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
fastapi-1        |   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 794, in invoke
fastapi-1        |     return callback(*args, **kwargs)
fastapi-1        |            ^^^^^^^^^^^^^^^^^^^^^^^^^
fastapi-1        |   File "/usr/local/lib/python3.11/site-packages/uvicorn/main.py", line 410, in main
fastapi-1        |     run(
fastapi-1        |   File "/usr/local/lib/python3.11/site-packages/uvicorn/main.py", line 577, in run
fastapi-1        |     server.run()
fastapi-1        |   File "/usr/local/lib/python3.11/site-packages/uvicorn/server.py", line 65, in run
fastapi-1        |     return asyncio.run(self.serve(sockets=sockets))
fastapi-1        |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
fastapi-1        |   File "/usr/local/lib/python3.11/asyncio/runners.py", line 190, in run
fastapi-1        |     return runner.run(main)
fastapi-1        |            ^^^^^^^^^^^^^^^^
fastapi-1        |   File "/usr/local/lib/python3.11/asyncio/runners.py", line 118, in run
fastapi-1        |     return self._loop.run_until_complete(task)
fastapi-1        |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
fastapi-1        |   File "/usr/local/lib/python3.11/asyncio/base_events.py", line 654, in run_until_complete
fastapi-1        |     return future.result()
fastapi-1        |            ^^^^^^^^^^^^^^^
fastapi-1        |   File "/usr/local/lib/python3.11/site-packages/uvicorn/server.py", line 69, in serve
fastapi-1        |     await self._serve(sockets)
fastapi-1        |   File "/usr/local/lib/python3.11/site-packages/uvicorn/server.py", line 76, in _serve
fastapi-1        |     config.load()
fastapi-1        |   File "/usr/local/lib/python3.11/site-packages/uvicorn/config.py", line 434, in load
fastapi-1        |     self.loaded_app = import_from_string(self.app)
fastapi-1        |                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
fastapi-1        |   File "/usr/local/lib/python3.11/site-packages/uvicorn/importer.py", line 22, in import_from_string
fastapi-1        |     raise exc from None
fastapi-1        |   File "/usr/local/lib/python3.11/site-packages/uvicorn/importer.py", line 19, in import_from_string
fastapi-1        |     module = importlib.import_module(module_str)
fastapi-1        |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
fastapi-1        |   File "/usr/local/lib/python3.11/importlib/__init__.py", line 126, in import_module
fastapi-1        |     return _bootstrap._gcd_import(name[level:], package, level)
fastapi-1        |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
fastapi-1        |   File "<frozen importlib._bootstrap>", line 1204, in _gcd_import
fastapi-1        |   File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
fastapi-1        |   File "<frozen importlib._bootstrap>", line 1147, in _find_and_load_unlocked
fastapi-1        |   File "<frozen importlib._bootstrap>", line 690, in _load_unlocked
fastapi-1        |   File "<frozen importlib._bootstrap_external>", line 940, in exec_module
fastapi-1        |   File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
fastapi-1        |   File "/app/app/main.py", line 8, in <module>
fastapi-1        |     from app.tasks import process_question_audio
fastapi-1        |   File "/app/app/tasks.py", line 1, in <module>
fastapi-1        |     import requests
fastapi-1        | ModuleNotFoundError: No module named 'requests'
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:36.078+00:00"},"s":"I",  "c":"WTRECOV",  "id":22430,   "ctx":"initandlisten","msg":"WiredTiger message","attr":{"message":{"ts_sec":1749635016,"ts_usec":78193,"thread":"1:0x7b6ac8909cc0","session_name":"txn-recover","category":"WT_VERB_RECOVERY_PROGRESS","category_id":30,"verbose_level":"DEBUG","verbose_level_id":1,"msg":"recovery log replay has successfully finished and ran for 438 milliseconds"}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:36.078+00:00"},"s":"I",  "c":"WTRECOV",  "id":22430,   "ctx":"initandlisten","msg":"WiredTiger message","attr":{"message":{"ts_sec":1749635016,"ts_usec":78363,"thread":"1:0x7b6ac8909cc0","session_name":"txn-recover","category":"WT_VERB_RECOVERY_PROGRESS","category_id":30,"verbose_level":"DEBUG","verbose_level_id":1,"msg":"Set global recovery timestamp: (0, 0)"}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:36.078+00:00"},"s":"I",  "c":"WTRECOV",  "id":22430,   "ctx":"initandlisten","msg":"WiredTiger message","attr":{"message":{"ts_sec":1749635016,"ts_usec":78408,"thread":"1:0x7b6ac8909cc0","session_name":"txn-recover","category":"WT_VERB_RECOVERY_PROGRESS","category_id":30,"verbose_level":"DEBUG","verbose_level_id":1,"msg":"Set global oldest timestamp: (0, 0)"}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:36.078+00:00"},"s":"I",  "c":"WTRECOV",  "id":22430,   "ctx":"initandlisten","msg":"WiredTiger message","attr":{"message":{"ts_sec":1749635016,"ts_usec":78925,"thread":"1:0x7b6ac8909cc0","session_name":"txn-recover","category":"WT_VERB_RECOVERY_PROGRESS","category_id":30,"verbose_level":"DEBUG","verbose_level_id":1,"msg":"recovery rollback to stable has successfully finished and ran for 0 milliseconds"}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:36.085+00:00"},"s":"I",  "c":"WTCHKPT",  "id":22430,   "ctx":"initandlisten","msg":"WiredTiger message","attr":{"message":{"ts_sec":1749635016,"ts_usec":85007,"thread":"1:0x7b6ac8909cc0","session_name":"WT_SESSION.checkpoint","category":"WT_VERB_CHECKPOINT_PROGRESS","category_id":6,"verbose_level":"DEBUG","verbose_level_id":1,"msg":"saving checkpoint snapshot min: 1, snapshot max: 1 snapshot count: 0, oldest timestamp: (0, 0) , meta checkpoint timestamp: (0, 0) base write gen: 72623"}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:36.090+00:00"},"s":"I",  "c":"WTRECOV",  "id":22430,   "ctx":"initandlisten","msg":"WiredTiger message","attr":{"message":{"ts_sec":1749635016,"ts_usec":90665,"thread":"1:0x7b6ac8909cc0","session_name":"txn-recover","category":"WT_VERB_RECOVERY_PROGRESS","category_id":30,"verbose_level":"DEBUG","verbose_level_id":1,"msg":"recovery checkpoint has successfully finished and ran for 11 milliseconds"}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:36.090+00:00"},"s":"I",  "c":"WTRECOV",  "id":22430,   "ctx":"initandlisten","msg":"WiredTiger message","attr":{"message":{"ts_sec":1749635016,"ts_usec":90724,"thread":"1:0x7b6ac8909cc0","session_name":"txn-recover","category":"WT_VERB_RECOVERY_PROGRESS","category_id":30,"verbose_level":"DEBUG","verbose_level_id":1,"msg":"recovery was completed successfully and took 451ms, including 438ms for the log replay, 0ms for the rollback to stable, and 11ms for the checkpoint."}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:36.091+00:00"},"s":"I",  "c":"STORAGE",  "id":4795906, "ctx":"initandlisten","msg":"WiredTiger opened","attr":{"durationMillis":938}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:36.091+00:00"},"s":"I",  "c":"RECOVERY", "id":23987,   "ctx":"initandlisten","msg":"WiredTiger recoveryTimestamp","attr":{"recoveryTimestamp":{"$timestamp":{"t":0,"i":0}}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:36.097+00:00"},"s":"W",  "c":"CONTROL",  "id":22120,   "ctx":"initandlisten","msg":"Access control is not enabled for the database. Read and write access to data and configuration is unrestricted","tags":["startupWarnings"]}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:36.098+00:00"},"s":"W",  "c":"CONTROL",  "id":22167,   "ctx":"initandlisten","msg":"You are running on a NUMA machine. We suggest launching mongod like this to avoid performance problems: numactl --interleave=all mongod [other options]","tags":["startupWarnings"]}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:36.099+00:00"},"s":"W",  "c":"CONTROL",  "id":5123300, "ctx":"initandlisten","msg":"vm.max_map_count is too low","attr":{"currentValue":1048576,"recommendedMinimum":1677720,"maxConns":838860},"tags":["startupWarnings"]}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:36.101+00:00"},"s":"I",  "c":"NETWORK",  "id":4915702, "ctx":"initandlisten","msg":"Updated wire specification","attr":{"oldSpec":{"incomingExternalClient":{"minWireVersion":0,"maxWireVersion":17},"incomingInternalClient":{"minWireVersion":0,"maxWireVersion":17},"outgoing":{"minWireVersion":6,"maxWireVersion":17},"isInternalClient":true},"newSpec":{"incomingExternalClient":{"minWireVersion":0,"maxWireVersion":17},"incomingInternalClient":{"minWireVersion":17,"maxWireVersion":17},"outgoing":{"minWireVersion":17,"maxWireVersion":17},"isInternalClient":true}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:36.101+00:00"},"s":"I",  "c":"REPL",     "id":5853300, "ctx":"initandlisten","msg":"current featureCompatibilityVersion value","attr":{"featureCompatibilityVersion":"6.0","context":"startup"}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:36.101+00:00"},"s":"I",  "c":"STORAGE",  "id":5071100, "ctx":"initandlisten","msg":"Clearing temp directory"}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:36.104+00:00"},"s":"I",  "c":"CONTROL",  "id":20536,   "ctx":"initandlisten","msg":"Flow Control is enabled on this deployment"}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:36.104+00:00"},"s":"I",  "c":"FTDC",     "id":20625,   "ctx":"initandlisten","msg":"Initializing full-time diagnostic data capture","attr":{"dataDirectory":"/data/db/diagnostic.data"}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:36.109+00:00"},"s":"I",  "c":"REPL",     "id":6015317, "ctx":"initandlisten","msg":"Setting new configuration state","attr":{"newState":"ConfigReplicationDisabled","oldState":"ConfigPreStart"}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:36.109+00:00"},"s":"I",  "c":"STORAGE",  "id":22262,   "ctx":"initandlisten","msg":"Timestamp monitor starting"}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:36.111+00:00"},"s":"I",  "c":"NETWORK",  "id":23015,   "ctx":"listener","msg":"Listening on","attr":{"address":"/tmp/mongodb-27017.sock"}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:36.111+00:00"},"s":"I",  "c":"NETWORK",  "id":23015,   "ctx":"listener","msg":"Listening on","attr":{"address":"0.0.0.0"}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:36.111+00:00"},"s":"I",  "c":"NETWORK",  "id":23016,   "ctx":"listener","msg":"Waiting for connections","attr":{"port":27017,"ssl":"off"}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:36.111+00:00"},"s":"I",  "c":"CONTROL",  "id":8423403, "ctx":"initandlisten","msg":"mongod startup complete","attr":{"Summary of time elapsed":{"Startup from clean shutdown?":true,"Statistics":{"Transport layer setup":"0 ms","Run initial syncer crash recovery":"0 ms","Create storage engine lock file in the data directory":"0 ms","Create storage engine lock file in the data directory":"0 ms","Get metadata describing storage engine":"0 ms","Get metadata describing storage engine":"0 ms","Validate options in metadata against current startup options":"0 ms","Validate options in metadata against current startup options":"0 ms","Create storage engine":"0 ms","Create storage engine":"939 ms","Write current PID to file":"0 ms","Write current PID to file":"0 ms","Initialize FCV before rebuilding indexes":"0 ms","Initialize FCV before rebuilding indexes":"2 ms","Drop abandoned idents and get back indexes that need to be rebuilt or builds that need to be restarted":"0 ms","Drop abandoned idents and get back indexes that need to be rebuilt or builds that need to be restarted":"0 ms","Rebuild indexes for collections":"0 ms","Rebuild indexes for collections":"0 ms","Build user and roles graph":"0 ms","Set up the background thread pool responsible for waiting for opTimes to be majority committed":"0 ms","Start up the replication coordinator":"3 ms","Start transport layer":"0 ms","_initAndListen total elapsed time":"960 ms"}}}}
fastapi-1 exited with code 1
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:45.438+00:00"},"s":"I",  "c":"NETWORK",  "id":22943,   "ctx":"listener","msg":"Connection accepted","attr":{"remote":"127.0.0.1:40754","uuid":"96637183-2e33-4162-b42a-b737d356336c","connectionId":1,"connectionCount":1}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:45.442+00:00"},"s":"I",  "c":"NETWORK",  "id":51800,   "ctx":"conn1","msg":"client metadata","attr":{"remote":"127.0.0.1:40754","client":"conn1","negotiatedCompressors":[],"doc":{"application":{"name":"mongosh 2.5.0"},"driver":{"name":"nodejs|mongosh","version":"6.14.2|2.5.0"},"platform":"Node.js v20.19.0, LE","os":{"name":"linux","architecture":"x64","version":"3.10.0-327.22.2.el7.x86_64","type":"Linux"},"env":{"container":{"runtime":"docker"}}}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:45.538+00:00"},"s":"I",  "c":"NETWORK",  "id":22943,   "ctx":"listener","msg":"Connection accepted","attr":{"remote":"127.0.0.1:40764","uuid":"1012d058-8b23-4024-ac21-5ace4c0820ca","connectionId":2,"connectionCount":2}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:45.539+00:00"},"s":"I",  "c":"NETWORK",  "id":22943,   "ctx":"listener","msg":"Connection accepted","attr":{"remote":"127.0.0.1:40772","uuid":"2b377307-eaac-4111-8462-4bfc0ccdb2c6","connectionId":3,"connectionCount":3}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:45.541+00:00"},"s":"I",  "c":"NETWORK",  "id":51800,   "ctx":"conn2","msg":"client metadata","attr":{"remote":"127.0.0.1:40764","client":"conn2","negotiatedCompressors":[],"doc":{"application":{"name":"mongosh 2.5.0"},"driver":{"name":"nodejs|mongosh","version":"6.14.2|2.5.0"},"platform":"Node.js v20.19.0, LE","os":{"name":"linux","architecture":"x64","version":"3.10.0-327.22.2.el7.x86_64","type":"Linux"},"env":{"container":{"runtime":"docker"}}}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:45.542+00:00"},"s":"I",  "c":"NETWORK",  "id":51800,   "ctx":"conn3","msg":"client metadata","attr":{"remote":"127.0.0.1:40772","client":"conn3","negotiatedCompressors":[],"doc":{"application":{"name":"mongosh 2.5.0"},"driver":{"name":"nodejs|mongosh","version":"6.14.2|2.5.0"},"platform":"Node.js v20.19.0, LE","os":{"name":"linux","architecture":"x64","version":"3.10.0-327.22.2.el7.x86_64","type":"Linux"},"env":{"container":{"runtime":"docker"}}}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:45.546+00:00"},"s":"I",  "c":"NETWORK",  "id":22943,   "ctx":"listener","msg":"Connection accepted","attr":{"remote":"127.0.0.1:40780","uuid":"467afc33-7891-487e-bcf0-4f7fcc37b888","connectionId":4,"connectionCount":4}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:45.550+00:00"},"s":"I",  "c":"NETWORK",  "id":22943,   "ctx":"listener","msg":"Connection accepted","attr":{"remote":"127.0.0.1:40790","uuid":"c319c52e-1519-4899-a0e7-87799c29bf3b","connectionId":5,"connectionCount":5}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:45.551+00:00"},"s":"I",  "c":"NETWORK",  "id":51800,   "ctx":"conn4","msg":"client metadata","attr":{"remote":"127.0.0.1:40780","client":"conn4","negotiatedCompressors":[],"doc":{"application":{"name":"mongosh 2.5.0"},"driver":{"name":"nodejs|mongosh","version":"6.14.2|2.5.0"},"platform":"Node.js v20.19.0, LE","os":{"name":"linux","architecture":"x64","version":"3.10.0-327.22.2.el7.x86_64","type":"Linux"},"env":{"container":{"runtime":"docker"}}}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:45.555+00:00"},"s":"I",  "c":"NETWORK",  "id":51800,   "ctx":"conn5","msg":"client metadata","attr":{"remote":"127.0.0.1:40790","client":"conn5","negotiatedCompressors":[],"doc":{"application":{"name":"mongosh 2.5.0"},"driver":{"name":"nodejs|mongosh","version":"6.14.2|2.5.0"},"platform":"Node.js v20.19.0, LE","os":{"name":"linux","architecture":"x64","version":"3.10.0-327.22.2.el7.x86_64","type":"Linux"},"env":{"container":{"runtime":"docker"}}}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:45.586+00:00"},"s":"I",  "c":"NETWORK",  "id":22944,   "ctx":"conn1","msg":"Connection ended","attr":{"remote":"127.0.0.1:40754","uuid":"96637183-2e33-4162-b42a-b737d356336c","connectionId":1,"connectionCount":4}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:45.586+00:00"},"s":"I",  "c":"NETWORK",  "id":22944,   "ctx":"conn3","msg":"Connection ended","attr":{"remote":"127.0.0.1:40772","uuid":"2b377307-eaac-4111-8462-4bfc0ccdb2c6","connectionId":3,"connectionCount":3}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:45.586+00:00"},"s":"I",  "c":"NETWORK",  "id":22944,   "ctx":"conn5","msg":"Connection ended","attr":{"remote":"127.0.0.1:40790","uuid":"c319c52e-1519-4899-a0e7-87799c29bf3b","connectionId":5,"connectionCount":1}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:45.586+00:00"},"s":"I",  "c":"NETWORK",  "id":22944,   "ctx":"conn2","msg":"Connection ended","attr":{"remote":"127.0.0.1:40764","uuid":"1012d058-8b23-4024-ac21-5ace4c0820ca","connectionId":2,"connectionCount":2}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:45.586+00:00"},"s":"I",  "c":"NETWORK",  "id":22944,   "ctx":"conn4","msg":"Connection ended","attr":{"remote":"127.0.0.1:40780","uuid":"467afc33-7891-487e-bcf0-4f7fcc37b888","connectionId":4,"connectionCount":0}}
mongo-express-1  | Waiting for mongo:27017...
mongo-express-1  | /docker-entrypoint.sh: line 15: mongo: Try again
mongo-express-1  | /docker-entrypoint.sh: line 15: /dev/tcp/mongo/27017: Invalid argument
mongo-express-1  | Wed Jun 11 09:43:51 UTC 2025 retrying to connect to mongo:27017 (2/10)
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:55.970+00:00"},"s":"I",  "c":"NETWORK",  "id":22943,   "ctx":"listener","msg":"Connection accepted","attr":{"remote":"127.0.0.1:45588","uuid":"411f0f7c-5118-4853-aabb-2ac523a5b54a","connectionId":6,"connectionCount":1}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:55.973+00:00"},"s":"I",  "c":"NETWORK",  "id":51800,   "ctx":"conn6","msg":"client metadata","attr":{"remote":"127.0.0.1:45588","client":"conn6","negotiatedCompressors":[],"doc":{"application":{"name":"mongosh 2.5.0"},"driver":{"name":"nodejs|mongosh","version":"6.14.2|2.5.0"},"platform":"Node.js v20.19.0, LE","os":{"name":"linux","architecture":"x64","version":"3.10.0-327.22.2.el7.x86_64","type":"Linux"},"env":{"container":{"runtime":"docker"}}}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:56.067+00:00"},"s":"I",  "c":"NETWORK",  "id":22943,   "ctx":"listener","msg":"Connection accepted","attr":{"remote":"127.0.0.1:45600","uuid":"3b3033d9-d8d1-4090-94e1-cc09676989e0","connectionId":7,"connectionCount":2}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:56.067+00:00"},"s":"I",  "c":"NETWORK",  "id":22943,   "ctx":"listener","msg":"Connection accepted","attr":{"remote":"127.0.0.1:45612","uuid":"6b125fae-1918-4b1f-940f-5073ad387212","connectionId":8,"connectionCount":3}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:56.069+00:00"},"s":"I",  "c":"NETWORK",  "id":51800,   "ctx":"conn7","msg":"client metadata","attr":{"remote":"127.0.0.1:45600","client":"conn7","negotiatedCompressors":[],"doc":{"application":{"name":"mongosh 2.5.0"},"driver":{"name":"nodejs|mongosh","version":"6.14.2|2.5.0"},"platform":"Node.js v20.19.0, LE","os":{"name":"linux","architecture":"x64","version":"3.10.0-327.22.2.el7.x86_64","type":"Linux"},"env":{"container":{"runtime":"docker"}}}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:56.070+00:00"},"s":"I",  "c":"NETWORK",  "id":51800,   "ctx":"conn8","msg":"client metadata","attr":{"remote":"127.0.0.1:45612","client":"conn8","negotiatedCompressors":[],"doc":{"application":{"name":"mongosh 2.5.0"},"driver":{"name":"nodejs|mongosh","version":"6.14.2|2.5.0"},"platform":"Node.js v20.19.0, LE","os":{"name":"linux","architecture":"x64","version":"3.10.0-327.22.2.el7.x86_64","type":"Linux"},"env":{"container":{"runtime":"docker"}}}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:56.072+00:00"},"s":"I",  "c":"NETWORK",  "id":22943,   "ctx":"listener","msg":"Connection accepted","attr":{"remote":"127.0.0.1:45626","uuid":"1148d092-4ad6-4f0f-88ef-c1baae119c3a","connectionId":9,"connectionCount":4}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:56.076+00:00"},"s":"I",  "c":"NETWORK",  "id":22943,   "ctx":"listener","msg":"Connection accepted","attr":{"remote":"127.0.0.1:45632","uuid":"22e3bf2d-8723-4dc1-8b35-423c3e2fd6e3","connectionId":10,"connectionCount":5}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:56.077+00:00"},"s":"I",  "c":"NETWORK",  "id":51800,   "ctx":"conn9","msg":"client metadata","attr":{"remote":"127.0.0.1:45626","client":"conn9","negotiatedCompressors":[],"doc":{"application":{"name":"mongosh 2.5.0"},"driver":{"name":"nodejs|mongosh","version":"6.14.2|2.5.0"},"platform":"Node.js v20.19.0, LE","os":{"name":"linux","architecture":"x64","version":"3.10.0-327.22.2.el7.x86_64","type":"Linux"},"env":{"container":{"runtime":"docker"}}}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:56.079+00:00"},"s":"I",  "c":"NETWORK",  "id":51800,   "ctx":"conn10","msg":"client metadata","attr":{"remote":"127.0.0.1:45632","client":"conn10","negotiatedCompressors":[],"doc":{"application":{"name":"mongosh 2.5.0"},"driver":{"name":"nodejs|mongosh","version":"6.14.2|2.5.0"},"platform":"Node.js v20.19.0, LE","os":{"name":"linux","architecture":"x64","version":"3.10.0-327.22.2.el7.x86_64","type":"Linux"},"env":{"container":{"runtime":"docker"}}}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:56.103+00:00"},"s":"I",  "c":"NETWORK",  "id":22944,   "ctx":"conn10","msg":"Connection ended","attr":{"remote":"127.0.0.1:45632","uuid":"22e3bf2d-8723-4dc1-8b35-423c3e2fd6e3","connectionId":10,"connectionCount":4}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:56.103+00:00"},"s":"I",  "c":"NETWORK",  "id":22944,   "ctx":"conn8","msg":"Connection ended","attr":{"remote":"127.0.0.1:45612","uuid":"6b125fae-1918-4b1f-940f-5073ad387212","connectionId":8,"connectionCount":3}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:56.103+00:00"},"s":"I",  "c":"NETWORK",  "id":22944,   "ctx":"conn9","msg":"Connection ended","attr":{"remote":"127.0.0.1:45626","uuid":"1148d092-4ad6-4f0f-88ef-c1baae119c3a","connectionId":9,"connectionCount":2}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:56.103+00:00"},"s":"I",  "c":"NETWORK",  "id":22944,   "ctx":"conn7","msg":"Connection ended","attr":{"remote":"127.0.0.1:45600","uuid":"3b3033d9-d8d1-4090-94e1-cc09676989e0","connectionId":7,"connectionCount":1}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:43:56.103+00:00"},"s":"I",  "c":"NETWORK",  "id":22944,   "ctx":"conn6","msg":"Connection ended","attr":{"remote":"127.0.0.1:45588","uuid":"411f0f7c-5118-4853-aabb-2ac523a5b54a","connectionId":6,"connectionCount":0}}
mongo-express-1  | /docker-entrypoint.sh: line 15: mongo: Try again
mongo-express-1  | /docker-entrypoint.sh: line 15: /dev/tcp/mongo/27017: Invalid argument
mongo-express-1  | Wed Jun 11 09:43:57 UTC 2025 retrying to connect to mongo:27017 (3/10)
mongo-express-1  | /docker-entrypoint.sh: line 15: mongo: Try again
mongo-express-1  | /docker-entrypoint.sh: line 15: /dev/tcp/mongo/27017: Invalid argument
mongo-express-1  | Wed Jun 11 09:44:03 UTC 2025 retrying to connect to mongo:27017 (4/10)
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:06.487+00:00"},"s":"I",  "c":"NETWORK",  "id":22943,   "ctx":"listener","msg":"Connection accepted","attr":{"remote":"127.0.0.1:41260","uuid":"73ae30bb-13f2-4eda-a37d-73a8c6a2ee75","connectionId":11,"connectionCount":1}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:06.490+00:00"},"s":"I",  "c":"NETWORK",  "id":51800,   "ctx":"conn11","msg":"client metadata","attr":{"remote":"127.0.0.1:41260","client":"conn11","negotiatedCompressors":[],"doc":{"application":{"name":"mongosh 2.5.0"},"driver":{"name":"nodejs|mongosh","version":"6.14.2|2.5.0"},"platform":"Node.js v20.19.0, LE","os":{"name":"linux","architecture":"x64","version":"3.10.0-327.22.2.el7.x86_64","type":"Linux"},"env":{"container":{"runtime":"docker"}}}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:06.555+00:00"},"s":"I",  "c":"NETWORK",  "id":22943,   "ctx":"listener","msg":"Connection accepted","attr":{"remote":"127.0.0.1:41274","uuid":"95d25342-b4cd-4aa9-a2c3-e91e62507b4a","connectionId":12,"connectionCount":2}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:06.555+00:00"},"s":"I",  "c":"NETWORK",  "id":22943,   "ctx":"listener","msg":"Connection accepted","attr":{"remote":"127.0.0.1:41290","uuid":"3d489724-5cd9-4ccc-823a-b6a26e5edce5","connectionId":13,"connectionCount":3}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:06.557+00:00"},"s":"I",  "c":"NETWORK",  "id":51800,   "ctx":"conn12","msg":"client metadata","attr":{"remote":"127.0.0.1:41274","client":"conn12","negotiatedCompressors":[],"doc":{"application":{"name":"mongosh 2.5.0"},"driver":{"name":"nodejs|mongosh","version":"6.14.2|2.5.0"},"platform":"Node.js v20.19.0, LE","os":{"name":"linux","architecture":"x64","version":"3.10.0-327.22.2.el7.x86_64","type":"Linux"},"env":{"container":{"runtime":"docker"}}}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:06.558+00:00"},"s":"I",  "c":"NETWORK",  "id":51800,   "ctx":"conn13","msg":"client metadata","attr":{"remote":"127.0.0.1:41290","client":"conn13","negotiatedCompressors":[],"doc":{"application":{"name":"mongosh 2.5.0"},"driver":{"name":"nodejs|mongosh","version":"6.14.2|2.5.0"},"platform":"Node.js v20.19.0, LE","os":{"name":"linux","architecture":"x64","version":"3.10.0-327.22.2.el7.x86_64","type":"Linux"},"env":{"container":{"runtime":"docker"}}}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:06.560+00:00"},"s":"I",  "c":"NETWORK",  "id":22943,   "ctx":"listener","msg":"Connection accepted","attr":{"remote":"127.0.0.1:41296","uuid":"4b7af2e0-31de-41ba-9862-7b47ea39712e","connectionId":14,"connectionCount":4}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:06.563+00:00"},"s":"I",  "c":"NETWORK",  "id":22943,   "ctx":"listener","msg":"Connection accepted","attr":{"remote":"127.0.0.1:41310","uuid":"f267d2d6-424f-465d-aa47-48fdc73776c0","connectionId":15,"connectionCount":5}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:06.564+00:00"},"s":"I",  "c":"NETWORK",  "id":51800,   "ctx":"conn14","msg":"client metadata","attr":{"remote":"127.0.0.1:41296","client":"conn14","negotiatedCompressors":[],"doc":{"application":{"name":"mongosh 2.5.0"},"driver":{"name":"nodejs|mongosh","version":"6.14.2|2.5.0"},"platform":"Node.js v20.19.0, LE","os":{"name":"linux","architecture":"x64","version":"3.10.0-327.22.2.el7.x86_64","type":"Linux"},"env":{"container":{"runtime":"docker"}}}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:06.567+00:00"},"s":"I",  "c":"NETWORK",  "id":51800,   "ctx":"conn15","msg":"client metadata","attr":{"remote":"127.0.0.1:41310","client":"conn15","negotiatedCompressors":[],"doc":{"application":{"name":"mongosh 2.5.0"},"driver":{"name":"nodejs|mongosh","version":"6.14.2|2.5.0"},"platform":"Node.js v20.19.0, LE","os":{"name":"linux","architecture":"x64","version":"3.10.0-327.22.2.el7.x86_64","type":"Linux"},"env":{"container":{"runtime":"docker"}}}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:06.595+00:00"},"s":"I",  "c":"NETWORK",  "id":22944,   "ctx":"conn15","msg":"Connection ended","attr":{"remote":"127.0.0.1:41310","uuid":"f267d2d6-424f-465d-aa47-48fdc73776c0","connectionId":15,"connectionCount":4}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:06.595+00:00"},"s":"I",  "c":"NETWORK",  "id":22944,   "ctx":"conn14","msg":"Connection ended","attr":{"remote":"127.0.0.1:41296","uuid":"4b7af2e0-31de-41ba-9862-7b47ea39712e","connectionId":14,"connectionCount":3}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:06.595+00:00"},"s":"I",  "c":"NETWORK",  "id":22944,   "ctx":"conn12","msg":"Connection ended","attr":{"remote":"127.0.0.1:41274","uuid":"95d25342-b4cd-4aa9-a2c3-e91e62507b4a","connectionId":12,"connectionCount":2}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:06.595+00:00"},"s":"I",  "c":"NETWORK",  "id":22944,   "ctx":"conn13","msg":"Connection ended","attr":{"remote":"127.0.0.1:41290","uuid":"3d489724-5cd9-4ccc-823a-b6a26e5edce5","connectionId":13,"connectionCount":1}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:06.595+00:00"},"s":"I",  "c":"NETWORK",  "id":22944,   "ctx":"conn11","msg":"Connection ended","attr":{"remote":"127.0.0.1:41260","uuid":"73ae30bb-13f2-4eda-a37d-73a8c6a2ee75","connectionId":11,"connectionCount":0}}
mongo-express-1  | /docker-entrypoint.sh: line 15: mongo: Try again
mongo-express-1  | /docker-entrypoint.sh: line 15: /dev/tcp/mongo/27017: Invalid argument
mongo-express-1  | Wed Jun 11 09:44:09 UTC 2025 retrying to connect to mongo:27017 (5/10)
mongo-express-1  | /docker-entrypoint.sh: line 15: mongo: Try again
mongo-express-1  | /docker-entrypoint.sh: line 15: /dev/tcp/mongo/27017: Invalid argument
mongo-express-1  | Wed Jun 11 09:44:15 UTC 2025 retrying to connect to mongo:27017 (6/10)
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:16.987+00:00"},"s":"I",  "c":"NETWORK",  "id":22943,   "ctx":"listener","msg":"Connection accepted","attr":{"remote":"127.0.0.1:52628","uuid":"e10b45cb-08a1-43e1-97b2-bb7f7574bb29","connectionId":16,"connectionCount":1}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:16.991+00:00"},"s":"I",  "c":"NETWORK",  "id":51800,   "ctx":"conn16","msg":"client metadata","attr":{"remote":"127.0.0.1:52628","client":"conn16","negotiatedCompressors":[],"doc":{"application":{"name":"mongosh 2.5.0"},"driver":{"name":"nodejs|mongosh","version":"6.14.2|2.5.0"},"platform":"Node.js v20.19.0, LE","os":{"name":"linux","architecture":"x64","version":"3.10.0-327.22.2.el7.x86_64","type":"Linux"},"env":{"container":{"runtime":"docker"}}}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:17.080+00:00"},"s":"I",  "c":"NETWORK",  "id":22943,   "ctx":"listener","msg":"Connection accepted","attr":{"remote":"127.0.0.1:52630","uuid":"40f0c99e-9c5e-4620-bdeb-00b829d5bda0","connectionId":17,"connectionCount":2}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:17.081+00:00"},"s":"I",  "c":"NETWORK",  "id":22943,   "ctx":"listener","msg":"Connection accepted","attr":{"remote":"127.0.0.1:52642","uuid":"ba4eb562-a9e5-4df0-8f0d-65a46f4fa139","connectionId":18,"connectionCount":3}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:17.083+00:00"},"s":"I",  "c":"NETWORK",  "id":51800,   "ctx":"conn17","msg":"client metadata","attr":{"remote":"127.0.0.1:52630","client":"conn17","negotiatedCompressors":[],"doc":{"application":{"name":"mongosh 2.5.0"},"driver":{"name":"nodejs|mongosh","version":"6.14.2|2.5.0"},"platform":"Node.js v20.19.0, LE","os":{"name":"linux","architecture":"x64","version":"3.10.0-327.22.2.el7.x86_64","type":"Linux"},"env":{"container":{"runtime":"docker"}}}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:17.084+00:00"},"s":"I",  "c":"NETWORK",  "id":51800,   "ctx":"conn18","msg":"client metadata","attr":{"remote":"127.0.0.1:52642","client":"conn18","negotiatedCompressors":[],"doc":{"application":{"name":"mongosh 2.5.0"},"driver":{"name":"nodejs|mongosh","version":"6.14.2|2.5.0"},"platform":"Node.js v20.19.0, LE","os":{"name":"linux","architecture":"x64","version":"3.10.0-327.22.2.el7.x86_64","type":"Linux"},"env":{"container":{"runtime":"docker"}}}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:17.087+00:00"},"s":"I",  "c":"NETWORK",  "id":22943,   "ctx":"listener","msg":"Connection accepted","attr":{"remote":"127.0.0.1:52656","uuid":"4121ea0c-f4db-4162-9582-596c5e0b9e18","connectionId":19,"connectionCount":4}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:17.091+00:00"},"s":"I",  "c":"NETWORK",  "id":22943,   "ctx":"listener","msg":"Connection accepted","attr":{"remote":"127.0.0.1:52668","uuid":"78d3a43c-4ff8-4217-ba27-8cfac554b684","connectionId":20,"connectionCount":5}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:17.091+00:00"},"s":"I",  "c":"NETWORK",  "id":51800,   "ctx":"conn19","msg":"client metadata","attr":{"remote":"127.0.0.1:52656","client":"conn19","negotiatedCompressors":[],"doc":{"application":{"name":"mongosh 2.5.0"},"driver":{"name":"nodejs|mongosh","version":"6.14.2|2.5.0"},"platform":"Node.js v20.19.0, LE","os":{"name":"linux","architecture":"x64","version":"3.10.0-327.22.2.el7.x86_64","type":"Linux"},"env":{"container":{"runtime":"docker"}}}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:17.095+00:00"},"s":"I",  "c":"NETWORK",  "id":51800,   "ctx":"conn20","msg":"client metadata","attr":{"remote":"127.0.0.1:52668","client":"conn20","negotiatedCompressors":[],"doc":{"application":{"name":"mongosh 2.5.0"},"driver":{"name":"nodejs|mongosh","version":"6.14.2|2.5.0"},"platform":"Node.js v20.19.0, LE","os":{"name":"linux","architecture":"x64","version":"3.10.0-327.22.2.el7.x86_64","type":"Linux"},"env":{"container":{"runtime":"docker"}}}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:17.125+00:00"},"s":"I",  "c":"NETWORK",  "id":22944,   "ctx":"conn18","msg":"Connection ended","attr":{"remote":"127.0.0.1:52642","uuid":"ba4eb562-a9e5-4df0-8f0d-65a46f4fa139","connectionId":18,"connectionCount":2}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:17.125+00:00"},"s":"I",  "c":"NETWORK",  "id":22944,   "ctx":"conn19","msg":"Connection ended","attr":{"remote":"127.0.0.1:52656","uuid":"4121ea0c-f4db-4162-9582-596c5e0b9e18","connectionId":19,"connectionCount":3}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:17.126+00:00"},"s":"I",  "c":"NETWORK",  "id":22944,   "ctx":"conn16","msg":"Connection ended","attr":{"remote":"127.0.0.1:52628","uuid":"e10b45cb-08a1-43e1-97b2-bb7f7574bb29","connectionId":16,"connectionCount":1}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:17.126+00:00"},"s":"I",  "c":"NETWORK",  "id":22944,   "ctx":"conn17","msg":"Connection ended","attr":{"remote":"127.0.0.1:52630","uuid":"40f0c99e-9c5e-4620-bdeb-00b829d5bda0","connectionId":17,"connectionCount":0}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:17.126+00:00"},"s":"I",  "c":"NETWORK",  "id":22944,   "ctx":"conn20","msg":"Connection ended","attr":{"remote":"127.0.0.1:52668","uuid":"78d3a43c-4ff8-4217-ba27-8cfac554b684","connectionId":20,"connectionCount":4}}
mongo-express-1  | /docker-entrypoint.sh: line 15: mongo: Try again
mongo-express-1  | /docker-entrypoint.sh: line 15: /dev/tcp/mongo/27017: Invalid argument
mongo-express-1  | Wed Jun 11 09:44:21 UTC 2025 retrying to connect to mongo:27017 (7/10)
mongo-express-1  | /docker-entrypoint.sh: line 15: mongo: Try again
mongo-express-1  | /docker-entrypoint.sh: line 15: /dev/tcp/mongo/27017: Invalid argument
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:27.500+00:00"},"s":"I",  "c":"NETWORK",  "id":22943,   "ctx":"listener","msg":"Connection accepted","attr":{"remote":"127.0.0.1:51178","uuid":"b293a381-3e80-464c-8658-30f3015bca1b","connectionId":21,"connectionCount":1}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:27.504+00:00"},"s":"I",  "c":"NETWORK",  "id":51800,   "ctx":"conn21","msg":"client metadata","attr":{"remote":"127.0.0.1:51178","client":"conn21","negotiatedCompressors":[],"doc":{"application":{"name":"mongosh 2.5.0"},"driver":{"name":"nodejs|mongosh","version":"6.14.2|2.5.0"},"platform":"Node.js v20.19.0, LE","os":{"name":"linux","architecture":"x64","version":"3.10.0-327.22.2.el7.x86_64","type":"Linux"},"env":{"container":{"runtime":"docker"}}}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:27.599+00:00"},"s":"I",  "c":"NETWORK",  "id":22943,   "ctx":"listener","msg":"Connection accepted","attr":{"remote":"127.0.0.1:51192","uuid":"cc7b01d6-7971-4bbb-ba26-8c9d67748c05","connectionId":22,"connectionCount":2}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:27.599+00:00"},"s":"I",  "c":"NETWORK",  "id":22943,   "ctx":"listener","msg":"Connection accepted","attr":{"remote":"127.0.0.1:51194","uuid":"5918284e-ac21-4c7b-ac9b-9e7457abd1d8","connectionId":23,"connectionCount":3}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:27.601+00:00"},"s":"I",  "c":"NETWORK",  "id":51800,   "ctx":"conn22","msg":"client metadata","attr":{"remote":"127.0.0.1:51192","client":"conn22","negotiatedCompressors":[],"doc":{"application":{"name":"mongosh 2.5.0"},"driver":{"name":"nodejs|mongosh","version":"6.14.2|2.5.0"},"platform":"Node.js v20.19.0, LE","os":{"name":"linux","architecture":"x64","version":"3.10.0-327.22.2.el7.x86_64","type":"Linux"},"env":{"container":{"runtime":"docker"}}}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:27.602+00:00"},"s":"I",  "c":"NETWORK",  "id":51800,   "ctx":"conn23","msg":"client metadata","attr":{"remote":"127.0.0.1:51194","client":"conn23","negotiatedCompressors":[],"doc":{"application":{"name":"mongosh 2.5.0"},"driver":{"name":"nodejs|mongosh","version":"6.14.2|2.5.0"},"platform":"Node.js v20.19.0, LE","os":{"name":"linux","architecture":"x64","version":"3.10.0-327.22.2.el7.x86_64","type":"Linux"},"env":{"container":{"runtime":"docker"}}}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:27.604+00:00"},"s":"I",  "c":"NETWORK",  "id":22943,   "ctx":"listener","msg":"Connection accepted","attr":{"remote":"127.0.0.1:51210","uuid":"1552ed38-881b-4ccb-a0e3-1168cfcd8374","connectionId":24,"connectionCount":4}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:27.607+00:00"},"s":"I",  "c":"NETWORK",  "id":22943,   "ctx":"listener","msg":"Connection accepted","attr":{"remote":"127.0.0.1:51224","uuid":"660e1292-3637-4149-99a1-ca165c7d0ecc","connectionId":25,"connectionCount":5}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:27.608+00:00"},"s":"I",  "c":"NETWORK",  "id":51800,   "ctx":"conn24","msg":"client metadata","attr":{"remote":"127.0.0.1:51210","client":"conn24","negotiatedCompressors":[],"doc":{"application":{"name":"mongosh 2.5.0"},"driver":{"name":"nodejs|mongosh","version":"6.14.2|2.5.0"},"platform":"Node.js v20.19.0, LE","os":{"name":"linux","architecture":"x64","version":"3.10.0-327.22.2.el7.x86_64","type":"Linux"},"env":{"container":{"runtime":"docker"}}}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:27.611+00:00"},"s":"I",  "c":"NETWORK",  "id":51800,   "ctx":"conn25","msg":"client metadata","attr":{"remote":"127.0.0.1:51224","client":"conn25","negotiatedCompressors":[],"doc":{"application":{"name":"mongosh 2.5.0"},"driver":{"name":"nodejs|mongosh","version":"6.14.2|2.5.0"},"platform":"Node.js v20.19.0, LE","os":{"name":"linux","architecture":"x64","version":"3.10.0-327.22.2.el7.x86_64","type":"Linux"},"env":{"container":{"runtime":"docker"}}}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:27.635+00:00"},"s":"I",  "c":"NETWORK",  "id":22944,   "ctx":"conn25","msg":"Connection ended","attr":{"remote":"127.0.0.1:51224","uuid":"660e1292-3637-4149-99a1-ca165c7d0ecc","connectionId":25,"connectionCount":4}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:27.635+00:00"},"s":"I",  "c":"NETWORK",  "id":22944,   "ctx":"conn22","msg":"Connection ended","attr":{"remote":"127.0.0.1:51192","uuid":"cc7b01d6-7971-4bbb-ba26-8c9d67748c05","connectionId":22,"connectionCount":1}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:27.635+00:00"},"s":"I",  "c":"NETWORK",  "id":22944,   "ctx":"conn24","msg":"Connection ended","attr":{"remote":"127.0.0.1:51210","uuid":"1552ed38-881b-4ccb-a0e3-1168cfcd8374","connectionId":24,"connectionCount":3}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:27.635+00:00"},"s":"I",  "c":"NETWORK",  "id":22944,   "ctx":"conn23","msg":"Connection ended","attr":{"remote":"127.0.0.1:51194","uuid":"5918284e-ac21-4c7b-ac9b-9e7457abd1d8","connectionId":23,"connectionCount":2}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:27.635+00:00"},"s":"I",  "c":"NETWORK",  "id":22944,   "ctx":"conn21","msg":"Connection ended","attr":{"remote":"127.0.0.1:51178","uuid":"b293a381-3e80-464c-8658-30f3015bca1b","connectionId":21,"connectionCount":0}}
mongo-express-1  | Wed Jun 11 09:44:27 UTC 2025 retrying to connect to mongo:27017 (8/10)
mongo-express-1  | /docker-entrypoint.sh: line 15: mongo: Try again
mongo-express-1  | /docker-entrypoint.sh: line 15: /dev/tcp/mongo/27017: Invalid argument
mongo-express-1  | Wed Jun 11 09:44:33 UTC 2025 retrying to connect to mongo:27017 (9/10)
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:36.098+00:00"},"s":"I",  "c":"WTCHKPT",  "id":22430,   "ctx":"Checkpointer","msg":"WiredTiger message","attr":{"message":{"ts_sec":1749635076,"ts_usec":98602,"thread":"1:0x7b6ac08f8640","session_name":"WT_SESSION.checkpoint","category":"WT_VERB_CHECKPOINT_PROGRESS","category_id":6,"verbose_level":"DEBUG","verbose_level_id":1,"msg":"saving checkpoint snapshot min: 3, snapshot max: 3 snapshot count: 0, oldest timestamp: (0, 0) , meta checkpoint timestamp: (0, 0) base write gen: 72623"}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:38.086+00:00"},"s":"I",  "c":"NETWORK",  "id":22943,   "ctx":"listener","msg":"Connection accepted","attr":{"remote":"127.0.0.1:52136","uuid":"af46288b-157f-45e1-9c52-d9f34502d37e","connectionId":26,"connectionCount":1}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:38.091+00:00"},"s":"I",  "c":"NETWORK",  "id":51800,   "ctx":"conn26","msg":"client metadata","attr":{"remote":"127.0.0.1:52136","client":"conn26","negotiatedCompressors":[],"doc":{"application":{"name":"mongosh 2.5.0"},"driver":{"name":"nodejs|mongosh","version":"6.14.2|2.5.0"},"platform":"Node.js v20.19.0, LE","os":{"name":"linux","architecture":"x64","version":"3.10.0-327.22.2.el7.x86_64","type":"Linux"},"env":{"container":{"runtime":"docker"}}}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:38.189+00:00"},"s":"I",  "c":"NETWORK",  "id":22943,   "ctx":"listener","msg":"Connection accepted","attr":{"remote":"127.0.0.1:52140","uuid":"b0a31f86-0853-4c1e-affa-906810e594b4","connectionId":27,"connectionCount":2}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:38.189+00:00"},"s":"I",  "c":"NETWORK",  "id":22943,   "ctx":"listener","msg":"Connection accepted","attr":{"remote":"127.0.0.1:52142","uuid":"0166dbdc-73f0-4630-93fc-05ceb90eba95","connectionId":28,"connectionCount":3}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:38.191+00:00"},"s":"I",  "c":"NETWORK",  "id":51800,   "ctx":"conn27","msg":"client metadata","attr":{"remote":"127.0.0.1:52140","client":"conn27","negotiatedCompressors":[],"doc":{"application":{"name":"mongosh 2.5.0"},"driver":{"name":"nodejs|mongosh","version":"6.14.2|2.5.0"},"platform":"Node.js v20.19.0, LE","os":{"name":"linux","architecture":"x64","version":"3.10.0-327.22.2.el7.x86_64","type":"Linux"},"env":{"container":{"runtime":"docker"}}}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:38.192+00:00"},"s":"I",  "c":"NETWORK",  "id":51800,   "ctx":"conn28","msg":"client metadata","attr":{"remote":"127.0.0.1:52142","client":"conn28","negotiatedCompressors":[],"doc":{"application":{"name":"mongosh 2.5.0"},"driver":{"name":"nodejs|mongosh","version":"6.14.2|2.5.0"},"platform":"Node.js v20.19.0, LE","os":{"name":"linux","architecture":"x64","version":"3.10.0-327.22.2.el7.x86_64","type":"Linux"},"env":{"container":{"runtime":"docker"}}}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:38.195+00:00"},"s":"I",  "c":"NETWORK",  "id":22943,   "ctx":"listener","msg":"Connection accepted","attr":{"remote":"127.0.0.1:52150","uuid":"caba5bf8-8e7e-4622-9399-339e30bdef45","connectionId":29,"connectionCount":4}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:38.197+00:00"},"s":"I",  "c":"NETWORK",  "id":22943,   "ctx":"listener","msg":"Connection accepted","attr":{"remote":"127.0.0.1:52160","uuid":"b62d8ca6-2b9a-4cdf-bf74-575a665c50cb","connectionId":30,"connectionCount":5}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:38.201+00:00"},"s":"I",  "c":"NETWORK",  "id":51800,   "ctx":"conn29","msg":"client metadata","attr":{"remote":"127.0.0.1:52150","client":"conn29","negotiatedCompressors":[],"doc":{"application":{"name":"mongosh 2.5.0"},"driver":{"name":"nodejs|mongosh","version":"6.14.2|2.5.0"},"platform":"Node.js v20.19.0, LE","os":{"name":"linux","architecture":"x64","version":"3.10.0-327.22.2.el7.x86_64","type":"Linux"},"env":{"container":{"runtime":"docker"}}}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:38.202+00:00"},"s":"I",  "c":"NETWORK",  "id":51800,   "ctx":"conn30","msg":"client metadata","attr":{"remote":"127.0.0.1:52160","client":"conn30","negotiatedCompressors":[],"doc":{"application":{"name":"mongosh 2.5.0"},"driver":{"name":"nodejs|mongosh","version":"6.14.2|2.5.0"},"platform":"Node.js v20.19.0, LE","os":{"name":"linux","architecture":"x64","version":"3.10.0-327.22.2.el7.x86_64","type":"Linux"},"env":{"container":{"runtime":"docker"}}}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:38.231+00:00"},"s":"I",  "c":"NETWORK",  "id":22944,   "ctx":"conn29","msg":"Connection ended","attr":{"remote":"127.0.0.1:52150","uuid":"caba5bf8-8e7e-4622-9399-339e30bdef45","connectionId":29,"connectionCount":4}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:38.231+00:00"},"s":"I",  "c":"NETWORK",  "id":22944,   "ctx":"conn26","msg":"Connection ended","attr":{"remote":"127.0.0.1:52136","uuid":"af46288b-157f-45e1-9c52-d9f34502d37e","connectionId":26,"connectionCount":2}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:38.231+00:00"},"s":"I",  "c":"NETWORK",  "id":22944,   "ctx":"conn28","msg":"Connection ended","attr":{"remote":"127.0.0.1:52142","uuid":"0166dbdc-73f0-4630-93fc-05ceb90eba95","connectionId":28,"connectionCount":3}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:38.231+00:00"},"s":"I",  "c":"NETWORK",  "id":22944,   "ctx":"conn27","msg":"Connection ended","attr":{"remote":"127.0.0.1:52140","uuid":"b0a31f86-0853-4c1e-affa-906810e594b4","connectionId":27,"connectionCount":0}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:38.231+00:00"},"s":"I",  "c":"NETWORK",  "id":22944,   "ctx":"conn30","msg":"Connection ended","attr":{"remote":"127.0.0.1:52160","uuid":"b62d8ca6-2b9a-4cdf-bf74-575a665c50cb","connectionId":30,"connectionCount":1}}
mongo-express-1  | /docker-entrypoint.sh: line 15: mongo: Try again
mongo-express-1  | /docker-entrypoint.sh: line 15: /dev/tcp/mongo/27017: Invalid argument
mongo-express-1  | Wed Jun 11 09:44:39 UTC 2025 retrying to connect to mongo:27017 (10/10)
mongo-express-1  | /docker-entrypoint.sh: line 15: mongo: Try again
mongo-express-1  | /docker-entrypoint.sh: line 15: /dev/tcp/mongo/27017: Invalid argument
mongo-express-1  | No custom config.js found, loading config.default.js
mongo-express-1  | Welcome to mongo-express 1.0.2
mongo-express-1  | ------------------------
mongo-express-1  | 
mongo-express-1  | 
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:45.652+00:00"},"s":"I",  "c":"NETWORK",  "id":22943,   "ctx":"listener","msg":"Connection accepted","attr":{"remote":"192.168.64.4:45674","uuid":"aa747beb-92d3-4773-b174-934668281628","connectionId":31,"connectionCount":1}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:45.659+00:00"},"s":"I",  "c":"NETWORK",  "id":51800,   "ctx":"conn31","msg":"client metadata","attr":{"remote":"192.168.64.4:45674","client":"conn31","negotiatedCompressors":[],"doc":{"driver":{"name":"nodejs","version":"4.13.0"},"os":{"type":"Linux","name":"linux","architecture":"x64","version":"6.8.0-60-generic"},"platform":"Node.js v18.20.3, LE (unified)|Node.js v18.20.3, LE (unified)"}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:45.679+00:00"},"s":"I",  "c":"NETWORK",  "id":22943,   "ctx":"listener","msg":"Connection accepted","attr":{"remote":"192.168.64.4:45676","uuid":"431fbe56-1e16-4671-bf29-bcab362b80b6","connectionId":32,"connectionCount":2}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:45.679+00:00"},"s":"I",  "c":"NETWORK",  "id":51800,   "ctx":"conn32","msg":"client metadata","attr":{"remote":"192.168.64.4:45676","client":"conn32","negotiatedCompressors":[],"doc":{"driver":{"name":"nodejs","version":"4.13.0"},"os":{"type":"Linux","name":"linux","architecture":"x64","version":"6.8.0-60-generic"},"platform":"Node.js v18.20.3, LE (unified)|Node.js v18.20.3, LE (unified)"}}}
mongo-express-1  | Mongo Express server listening at http://0.0.0.0:8081
mongo-express-1  | Server is open to allow connections from anyone (0.0.0.0)
mongo-express-1  | Basic authentication is disabled. It is recommended to set the useBasicAuth to true in the config.js.
mongodb-1        | {"t":{"$date":"2025-06-11T09:44:48.668+00:00"},"s":"I",  "c":"NETWORK",  "id":22943,   "ctx":"listener","msg":"Connection accepted","attr":{"remot







