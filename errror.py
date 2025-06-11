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
 ✔ Container interview-system-fastapi-1        Removed                                                                                                  0.0s 
 ✔ Container interview-system-celery-1         Removed                                                                                                  0.0s 
 ✔ Container interview-system-mongo-express-1  Removed                                                                                                  0.0s 
 ✔ Container interview-system-redis-1          Removed                                                                                                  0.0s 
 ✔ Container interview-system-mongodb-1        Removed                                                                                                  0.0s 
 ✔ Network interview-system_interview-network  Removed                                                                                                  0.2s 
yaz@gpu:~/interview-system$ docker compose up --build
Compose can now delegate builds to bake for better performance.
 To do so, set COMPOSE_BAKE=true.
[+] Building 0.7s (16/19)                                                                                                                     docker:default
 => [fastapi internal] load build definition from Dockerfile                                                                                            0.0s
 => => transferring dockerfile: 240B                                                                                                                    0.0s
 => [celery internal] load build definition from Dockerfile                                                                                             0.0s
 => => transferring dockerfile: 240B                                                                                                                    0.0s
 => [celery internal] load metadata for docker.io/library/python:3.11-slim                                                                              0.6s
 => [fastapi internal] load .dockerignore                                                                                                               0.0s
 => => transferring context: 2B                                                                                                                         0.0s
 => [celery internal] load .dockerignore                                                                                                                0.0s
 => => transferring context: 2B                                                                                                                         0.0s
 => [fastapi 1/5] FROM docker.io/library/python:3.11-slim@sha256:74132ced0002947303bc75654c7d51d3818435fe1c0ec6e4d84f7ca4d0849878                       0.0s
 => => resolve docker.io/library/python:3.11-slim@sha256:74132ced0002947303bc75654c7d51d3818435fe1c0ec6e4d84f7ca4d0849878                               0.0s
 => [celery internal] load build context                                                                                                                0.0s
 => => transferring context: 475B                                                                                                                       0.0s
 => [fastapi internal] load build context                                                                                                               0.0s
 => => transferring context: 475B                                                                                                                       0.0s
 => CACHED [celery 2/5] WORKDIR /app                                                                                                                    0.0s
 => CACHED [celery 3/5] COPY requirements.txt .                                                                                                         0.0s
 => CACHED [celery 4/5] RUN pip install --no-cache-dir -r requirements.txt                                                                              0.0s
 => CACHED [fastapi 5/5] COPY app/ ./app/                                                                                                               0.0s
 => [celery] exporting to image                                                                                                                         0.0s
 => => exporting layers                                                                                                                                 0.0s
 => => writing image sha256:1f46c94474309813549bf6564a5023f86a13f9d6ef041dafd8ca95b7edafb5da                                                            0.0s
 => => naming to docker.io/library/interview-system-celery                                                                                              0.0s
 => [fastapi] exporting to image                                                                                                                        0.0s
 => => exporting layers                                                                                                                                 0.0s
 => => writing image sha256:47733b1dd49fab7be95287f0f832e174be78a60afb09b5954e2b98221e810613                                                            0.0s
 => => naming to docker.io/library/interview-system-fastapi                                                                                             0.0s
 => [celery] resolving provenance for metadata file                                                                                                     0.0s
 => [fastapi] resolving provenance for metadata file                                                                                                    0.0s
[+] Running 8/8
 ✔ celery                                      Built                                                                                                    0.0s 
 ✔ fastapi                                     Built                                                                                                    0.0s 
 ✔ Network interview-system_interview-network  Created                                                                                                  0.1s 
 ✔ Container interview-system-mongodb-1        Created                                                                                                  0.0s 
 ✔ Container interview-system-redis-1          Created                                                                                                  0.0s 
 ✔ Container interview-system-celery-1         Created                                                                                                  0.0s 
 ✔ Container interview-system-fastapi-1        Created                                                                                                  0.0s 
 ✔ Container interview-system-mongo-express-1  Created                                                                                                  0.0s 
Attaching to celery-1, fastapi-1, mongo-express-1, mongodb-1, redis-1
redis-1          | 1:C 11 Jun 2025 09:39:32.643 # oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
redis-1          | 1:C 11 Jun 2025 09:39:32.643 # Redis version=7.0.15, bits=64, commit=00000000, modified=0, pid=1, just started
redis-1          | 1:C 11 Jun 2025 09:39:32.643 # Warning: no config file specified, using the default config. In order to specify a config file use redis-server /path/to/redis.conf
redis-1          | 1:M 11 Jun 2025 09:39:32.644 * monotonic clock: POSIX clock_gettime
redis-1          | 1:M 11 Jun 2025 09:39:32.646 * Running mode=standalone, port=6379.
redis-1          | 1:M 11 Jun 2025 09:39:32.646 # Server initialized
redis-1          | 1:M 11 Jun 2025 09:39:32.646 # WARNING Memory overcommit must be enabled! Without it, a background save or replication may fail under low memory condition. Being disabled, it can can also cause failures without low memory condition, see https://github.com/jemalloc/jemalloc/issues/1328. To fix this issue add 'vm.overcommit_memory = 1' to /etc/sysctl.conf and then reboot or run the command 'sysctl vm.overcommit_memory=1' for this to take effect.
redis-1          | 1:M 11 Jun 2025 09:39:32.647 * Ready to accept connections
mongodb-1        | {"t":{"$date":"2025-06-11T09:39:32.744+00:00"},"s":"I",  "c":"NETWORK",  "id":4915701, "ctx":"-","msg":"Initialized wire specification","attr":{"spec":{"incomingExternalClient":{"minWireVersion":0,"maxWireVersion":17},"incomingInternalClient":{"minWireVersion":0,"maxWireVersion":17},"outgoing":{"minWireVersion":6,"maxWireVersion":17},"isInternalClient":true}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:39:32.744+00:00"},"s":"I",  "c":"CONTROL",  "id":23285,   "ctx":"-","msg":"Automatically disabling TLS 1.0, to force-enable TLS 1.0 specify --sslDisabledProtocols 'none'"}
mongodb-1        | {"t":{"$date":"2025-06-11T09:39:32.746+00:00"},"s":"I",  "c":"NETWORK",  "id":4648601, "ctx":"main","msg":"Implicit TCP FastOpen unavailable. If TCP FastOpen is required, set tcpFastOpenServer, tcpFastOpenClient, and tcpFastOpenQueueSize."}
mongodb-1        | {"t":{"$date":"2025-06-11T09:39:32.747+00:00"},"s":"I",  "c":"REPL",     "id":5123008, "ctx":"main","msg":"Successfully registered PrimaryOnlyService","attr":{"service":"TenantMigrationDonorService","namespace":"config.tenantMigrationDonors"}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:39:32.747+00:00"},"s":"I",  "c":"REPL",     "id":5123008, "ctx":"main","msg":"Successfully registered PrimaryOnlyService","attr":{"service":"TenantMigrationRecipientService","namespace":"config.tenantMigrationRecipients"}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:39:32.747+00:00"},"s":"I",  "c":"REPL",     "id":5123008, "ctx":"main","msg":"Successfully registered PrimaryOnlyService","attr":{"service":"ShardSplitDonorService","namespace":"config.tenantSplitDonors"}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:39:32.747+00:00"},"s":"I",  "c":"CONTROL",  "id":5945603, "ctx":"main","msg":"Multi threading initialized"}
mongodb-1        | {"t":{"$date":"2025-06-11T09:39:32.748+00:00"},"s":"I",  "c":"CONTROL",  "id":4615611, "ctx":"initandlisten","msg":"MongoDB starting","attr":{"pid":1,"port":27017,"dbPath":"/data/db","architecture":"64-bit","host":"171b260870eb"}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:39:32.748+00:00"},"s":"I",  "c":"CONTROL",  "id":23403,   "ctx":"initandlisten","msg":"Build Info","attr":{"buildInfo":{"version":"6.0.22","gitVersion":"ee527360b84c6798535ee0895de3c7186b3522f9","openSSLVersion":"OpenSSL 3.0.2 15 Mar 2022","modules":[],"allocator":"tcmalloc","environment":{"distmod":"ubuntu2204","distarch":"x86_64","target_arch":"x86_64"}}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:39:32.748+00:00"},"s":"I",  "c":"CONTROL",  "id":51765,   "ctx":"initandlisten","msg":"Operating System","attr":{"os":{"name":"Ubuntu","version":"22.04"}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:39:32.748+00:00"},"s":"I",  "c":"CONTROL",  "id":21951,   "ctx":"initandlisten","msg":"Options set by command line","attr":{"options":{"net":{"bindIp":"*"}}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:39:32.750+00:00"},"s":"I",  "c":"STORAGE",  "id":22270,   "ctx":"initandlisten","msg":"Storage engine to use detected by data files","attr":{"dbpath":"/data/db","storageEngine":"wiredTiger"}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:39:32.750+00:00"},"s":"I",  "c":"STORAGE",  "id":22297,   "ctx":"initandlisten","msg":"Using the XFS filesystem is strongly recommended with the WiredTiger storage engine. See http://dochub.mongodb.org/core/prodnotes-filesystem","tags":["startupWarnings"]}
mongodb-1        | {"t":{"$date":"2025-06-11T09:39:32.750+00:00"},"s":"I",  "c":"STORAGE",  "id":22315,   "ctx":"initandlisten","msg":"Opening WiredTiger","attr":{"config":"create,cache_size=63752M,session_max=33000,eviction=(threads_min=4,threads_max=4),config_base=false,statistics=(fast),log=(enabled=true,remove=true,path=journal,compressor=snappy),builtin_extension_config=(zstd=(compression_level=6)),file_manager=(close_idle_time=600,close_scan_interval=10,close_handle_minimum=2000),statistics_log=(wait=0),json_output=(error,message),verbose=[recovery_progress:1,checkpoint_progress:1,compact_progress:1,backup:0,checkpoint:0,compact:0,evict:0,history_store:0,recovery:0,rts:0,salvage:0,tiered:0,timestamp:0,transaction:0,verify:0,log:0],"}}
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
mongodb-1        | {"t":{"$date":"2025-06-11T09:39:33.243+00:00"},"s":"I",  "c":"WTRECOV",  "id":22430,   "ctx":"initandlisten","msg":"WiredTiger message","attr":{"message":{"ts_sec":1749634773,"ts_usec":243330,"thread":"1:0x7ca3c5f67cc0","session_name":"txn-recover","category":"WT_VERB_RECOVERY_PROGRESS","category_id":30,"verbose_level":"DEBUG","verbose_level_id":1,"msg":"Recovering log 9 through 10"}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:39:33.308+00:00"},"s":"I",  "c":"WTRECOV",  "id":22430,   "ctx":"initandlisten","msg":"WiredTiger message","attr":{"message":{"ts_sec":1749634773,"ts_usec":308071,"thread":"1:0x7ca3c5f67cc0","session_name":"txn-recover","category":"WT_VERB_RECOVERY_PROGRESS","category_id":30,"verbose_level":"DEBUG","verbose_level_id":1,"msg":"Recovering log 10 through 10"}}}
celery-1 exited with code 2
mongodb-1        | {"t":{"$date":"2025-06-11T09:39:33.406+00:00"},"s":"I",  "c":"WTRECOV",  "id":22430,   "ctx":"initandlisten","msg":"WiredTiger message","attr":{"message":{"ts_sec":1749634773,"ts_usec":405988,"thread":"1:0x7ca3c5f67cc0","session_name":"txn-recover","category":"WT_VERB_RECOVERY_PROGRESS","category_id":30,"verbose_level":"DEBUG","verbose_level_id":1,"msg":"Main recovery loop: starting at 9/5376 to 10/256"}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:39:33.518+00:00"},"s":"I",  "c":"WTRECOV",  "id":22430,   "ctx":"initandlisten","msg":"WiredTiger message","attr":{"message":{"ts_sec":1749634773,"ts_usec":518624,"thread":"1:0x7ca3c5f67cc0","session_name":"txn-recover","category":"WT_VERB_RECOVERY_PROGRESS","category_id":30,"verbose_level":"DEBUG","verbose_level_id":1,"msg":"Recovering log 9 through 10"}}}
mongodb-1        | {"t":{"$date":"2025-06-11T09:39:33.586+00:00"},"s":"I",  "c":"WTRECOV",  "id":22430,   "ctx":"initandlisten","msg":"WiredTiger message","attr":{"message":{"ts_sec":1749634773,"ts_usec":586187,"thread":"1:0x7ca3c5f67cc0","session_name":"txn-recover","category":"WT_VERB_RECOVERY_PROGRESS","category_id":30,"verbose_level":"DEBUG","verbose_level_id":1,"msg":"Recovering log 10 through 10"}}}
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
mongodb-1        | {"t":{"$date":"2025-06-11T09:39:33.631+00:00"},"s":"I",  "c":"WTRECOV",  "id":22430,   "ctx":"initandlisten","msg":"WiredTiger message","attr":{"message":{"ts_sec":1749634773,"ts_usec":631064,"thread":"1:0x7ca3c5f67cc0","session_name":"txn-recover","category":"WT_VERB_RECOVERY_PROGRESS","category_id":30,"verbose_level":"DEBUG","verbose_level_id":1,"msg":"recovery log replay has successfully finished and ran for 388 milliseconds"}}}
fastapi-1        |     run(
mongodb-1        | {"t":{"$date":"2025-06-11T09:39:33.631+00:00"},"s":"I",  "c":"WTRECOV",  "id":22430,   "ctx":"initandlisten","msg":"WiredTiger message","attr":{"message":{"ts_sec":1749634773,"ts_usec":631165,"thread":"1:0x7ca3c5f67cc0","session_name":"txn-recover","category":"WT_VERB_RECOVERY_PROGRESS","category_id":30,"verbose_level":"DEBUG","verbose_level_id":1,"msg":"Set global recovery timestamp: (0, 0)"}}}
fastapi-1        |   File "/usr/local/lib/python3.11/site-packages/uvicorn/main.py", line 577, in run
mongodb-1        | {"t":{"$date":"2025-06-11T09:39:33.631+00:00"},"s":"I",  "c":"WTRECOV",  "id":22430,   "ctx":"initandlisten","msg":"WiredTiger message","attr":{"message":{"ts_sec":1749634773,"ts_usec":631183,"thread":"1:0x7ca3c5f67cc0","session_name":"txn-recover","category":"WT_VERB_RECOVERY_PROGRESS","category_id":30,"verbose_level":"DEBUG","verbose_level_id":1,"msg":"Set global oldest timestamp: (0, 0)"}}}
fastapi-1        |     server.run()
mongodb-1        | {"t":{"$date":"2025-06-11T09:39:33.631+00:00"},"s":"I",  "c":"WTRECOV",  "id":22430,   "ctx":"initandlisten","msg":"WiredTiger message","attr":{"message":{"ts_sec":1749634773,"ts_usec":631461,"thread":"1:0x7ca3c5f67cc0","session_name":"txn-recover","category":"WT_VERB_RECOVERY_PROGRESS","category_id":30,"verbose_level":"DEBUG","verbose_level_id":1,"msg":"recovery rollback to stable has successfully finished and ran for 0 milliseconds"}}}
fastapi-1        |   File "/usr/local/lib/python3.11/site-packages/uvicorn/server.py", line 65, in run
mongodb-1        | {"t":{"$date":"2025-06-11T09:39:33.634+00:00"},"s":"I",  "c":"WTCHKPT",  "id":22430,   "ctx":"initandlisten","msg":"WiredTiger message","attr":{"message":{"ts_sec":1749634773,"ts_usec":634400,"thread":"1:0x7ca3c5f67cc0","session_name":"WT_SESSION.checkpoint","category":"WT_VERB_CHECKPOINT_PROGRESS","category_id":6,"verbose_level":"DEBUG","verbose_level_id":1,"msg":"saving checkpoint snapshot min: 1, snapshot max: 1 snapshot count: 0, oldest timestamp: (0, 0) , meta checkpoint timestamp: (0, 0) base write gen: 72606"}}}
fastapi-1        |     return asyncio.run(self.serve(sockets=sockets))
fastapi-1        |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
fastapi-1        |   File "/usr/local/lib/python3.11/asyncio/runners.py", line 190, in run
fastapi-1        |     return runner.run(main)
fastapi-1        |            ^^^^^^^^^^^^^^^^
mongodb-1        | {"t":{"$date":"2025-06-11T09:39:33.636+00:00"},"s":"I",  "c":"WTRECOV",  "id":22430,   "ctx":"initandlisten","msg":"WiredTiger message","attr":{"message":{"ts_sec":1749634773,"ts_usec":636456,"thread":"1:0x7ca3c5f67cc0","session_name":"txn-recover","category":"WT_VERB_RECOVERY_PROGRESS","category_id":30,"verbose_level":"DEBUG","verbose_level_id":1,"msg":"recovery checkpoint has successfully finished and ran for 4 milliseconds"}}}
fastapi-1        |   File "/usr/local/lib/python3.11/asyncio/runners.py", line 118, in run
mongodb-1        | {"t":{"$date":"2025-06-11T09:39:33.636+00:00"},"s":"I",  "c":"WTRECOV",  "id":22430,   "ctx":"initandlisten","msg":"WiredTiger message","attr":{"message":{"ts_sec":1749634773,"ts_usec":636516,"thread":"1:0x7ca3c5f67cc0","session_name":"txn-recover","category":"WT_VERB_RECOVERY_PROGRESS","category_id":30,"verbose_level":"DEBUG","verbose_level_id":1,"msg":"recovery was completed successfully and took 393ms, including 388ms for the log replay, 0ms for the rollback to stable, and 4ms for the checkpoint."}}}
fastapi-1        |     return self._loop.run_until_complete(task)
mongodb-1        | {"t":{"$date":"2025-06-11T09:39:33.637+00:00"},"s":"I",  "c":"STORAGE",  "id":4795906, "ctx":"initandlisten","msg":"WiredTiger opened","attr":{"durationMillis":887}}
fastapi-1        |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
mongodb-1        | {"t":{"$date":"2025-06-11T09:39:33.637+00:00"},"s":"I",  "c":"RECOVERY", "id":23987,   "ctx":"initandlisten","msg":"WiredTiger recoveryTimestamp","attr":{"recoveryTimestamp":{"$timestamp":{"t":0,"i":0}}}}
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
mongodb-1        | {"t":{"$date":"2025-06-11T09:39:33.643+00:00"},"s":"W",  "c":"CONTROL",  "id":22120,   "ctx":"initandlisten","msg":"Access control is not enabled for the database. Read and write access to data and configuration is unrestricted","tags":["startupWarnings"]}
fastapi-1        |   File "/usr/local/lib/python3.11/site-packages/uvicorn/importer.py", line 22, in import_from_string
mongodb-1        | {"t":{"$date":"2025-06-11T09:39:33.646+00:00"},"s":"W",  "c":"CONTROL",  "id":22167,   "ctx":"initandlisten","msg":"You are running on a NUMA machine. We suggest launching mongod like this to avoid performance problems: numactl --interleave=all mongod [other options]","tags":["startupWarnings"]}
fastapi-1        |     raise exc from None
mongodb-1        | {"t":{"$date":"2025-06-11T09:39:33.646+00:00"},"s":"W",  "c":"CONTROL",  "id":5123300, "ctx":"initandlisten","msg":"vm.max_map_count is too low","attr":{"currentValue":1048576,"recommendedMinimum":1677720,"maxConns":838860},"tags":["startupWarnings"]}
fastapi-1        |   File "/usr/local/lib/python3.11/site-packages/uvicorn/importer.py", line 19, in import_from_string
fastapi-1        |     module = importlib.import_module(module_str)
mongodb-1        | {"t":{"$date":"2025-06-11T09:39:33.649+00:00"},"s":"I",  "c":"NETWORK",  "id":4915702, "ctx":"initandlisten","msg":"Updated wire specification","attr":{"oldSpec":{"incomingExternalClient":{"minWireVersion":0,"maxWireVersion":17},"incomingInternalClient":{"minWireVersion":0,"maxWireVersion":17},"outgoing":{"minWireVersion":6,"maxWireVersion":17},"isInternalClient":true},"newSpec":{"incomingExternalClient":{"minWireVersion":0,"maxWireVersion":17},"incomingInternalClient":{"minWireVersion":17,"maxWireVersion":17},"outgoing":{"minWireVersion":17,"maxWireVersion":17},"isInternalClient":true}}}
fastapi-1        |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
mongodb-1        | {"t":{"$date":"2025-06-11T09:39:33.649+00:00"},"s":"I",  "c":"REPL",     "id":5853300, "ctx":"initandlisten","msg":"current featureCompatibilityVersion value","attr":{"featureCompatibilityVersion":"6.0","context":"startup"}}
fastapi-1        |   File "/usr/local/lib/python3.11/importlib/__init__.py", line 126, in import_module
mongodb-1        | {"t":{"$date":"2025-06-11T09:39:33.649+00:00"},"s":"I",  "c":"STORAGE",  "id":5071100, "ctx":"initandlisten","msg":"Clearing temp directory"}
fastapi-1        |     return _bootstrap._gcd_import(name[level:], package, level)
mongodb-1        | {"t":{"$date":"2025-06-11T09:39:33.651+00:00"},"s":"I",  "c":"CONTROL",  "id":20536,   "ctx":"initandlisten","msg":"Flow Control is enabled on this deployment"}
fastapi-1        |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
mongodb-1        | {"t":{"$date":"2025-06-11T09:39:33.652+00:00"},"s":"I",  "c":"FTDC",     "id":20625,   "ctx":"initandlisten","msg":"Initializing full-time diagnostic data capture","attr":{"dataDirectory":"/data/db/diagnostic.data"}}
fastapi-1        |   File "<frozen importlib._bootstrap>", line 1204, in _gcd_import
fastapi-1        |   File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
mongodb-1        | {"t":{"$date":"2025-06-11T09:39:33.655+00:00"},"s":"I",  "c":"REPL",     "id":6015317, "ctx":"initandlisten","msg":"Setting new configuration state","attr":{"newState":"ConfigReplicationDisabled","oldState":"ConfigPreStart"}}
fastapi-1        |   File "<frozen importlib._bootstrap>", line 1147, in _find_and_load_unlocked
mongodb-1        | {"t":{"$date":"2025-06-11T09:39:33.656+00:00"},"s":"I",  "c":"STORAGE",  "id":22262,   "ctx":"initandlisten","msg":"Timestamp monitor starting"}
fastapi-1        |   File "<frozen importlib._bootstrap>", line 690, in _load_unlocked
mongodb-1        | {"t":{"$date":"2025-06-11T09:39:33.657+00:00"},"s":"I",  "c":"NETWORK",  "id":23015,   "ctx":"listener","msg":"Listening on","attr":{"address":"/tmp/mongodb-27017.sock"}}
fastapi-1        |   File "<frozen importlib._bootstrap_external>", line 940, in exec_module
mongodb-1        | {"t":{"$date":"2025-06-11T09:39:33.657+00:00"},"s":"I",  "c":"NETWORK",  "id":23015,   "ctx":"listener","msg":"Listening on","attr":{"address":"0.0.0.0"}}
fastapi-1        |   File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
mongodb-1        | {"t":{"$date":"2025-06-11T09:39:33.657+00:00"},"s":"I",  "c":"NETWORK",  "id":23016,   "ctx":"listener","msg":"Waiting for connections","attr":{"port":27017,"ssl":"off"}}
fastapi-1        |   File "/app/app/main.py", line 8, in <module>
mongodb-1        | {"t":{"$date":"2025-06-11T09:39:33.657+00:00"},"s":"I",  "c":"CONTROL",  "id":8423403, "ctx":"initandlisten","msg":"mongod startup complete","attr":{"Summary of time elapsed":{"Startup from clean shutdown?":true,"Statistics":{"Transport layer setup":"0 ms","Run initial syncer crash recovery":"0 ms","Create storage engine lock file in the data directory":"0 ms","Create storage engine lock file in the data directory":"0 ms","Get metadata describing storage engine":"0 ms","Get metadata describing storage engine":"0 ms","Validate options in metadata against current startup options":"0 ms","Validate options in metadata against current startup options":"0 ms","Create storage engine":"0 ms","Create storage engine":"888 ms","Write current PID to file":"0 ms","Write current PID to file":"0 ms","Initialize FCV before rebuilding indexes":"0 ms","Initialize FCV before rebuilding indexes":"3 ms","Drop abandoned idents and get back indexes that need to be rebuilt or builds that need to be restarted":"0 ms","Drop abandoned idents and get back indexes that need to be rebuilt or builds that need to be restarted":"0 ms","Rebuild indexes for collections":"0 ms","Rebuild indexes for collections":"0 ms","Build user and roles graph":"0 ms","Set up the background thread pool responsible for waiting for opTimes to be majority committed":"0 ms","Start up the replication coordinator":"2 ms","Start transport layer":"0 ms","_initAndListen total elapsed time":"909 ms"}}}}
fastapi-1        |     from app.tasks import process_question_audio
fastapi-1        |   File "/app/app/tasks.py", line 1, in <module>
fastapi-1        |     import requests
fastapi-1        | ModuleNotFoundError: No module named 'requests'
fastapi-1 exited with code 1
mongodb














