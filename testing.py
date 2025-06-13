from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from typing import List , Optional, Union  
from app.models import Interview, Question
from app.tasks import process_question_audio 
from app.tasks import process_question_video
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
    audio_file: UploadFile = File(...),
    video_file: UploadFile = File(...)  # 👈 NOW REQUIRED
):
    # 🎙️ Read audio
    audio_bytes = await audio_file.read()

    # 🎬 Read video
    video_bytes = await video_file.read()
    print(f"📹 Received video bytes: {len(video_bytes)}")

    # 🔎 Get interview from DB
    interview = interviews_collection.find_one({"_id": ObjectId(interview_id)})
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    session_id = interview["session_id"]

    # 🧠 Get next question from LLM
    try:
        llm_resp = requests.post(
            "http://10.100.102.6:8906/next_question",
            json={"session_id": session_id, "answer": "placeholder"}
        )
        llm_data = llm_resp.json()
        new_question_text = llm_data.get("question", "")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")

    # 🔢 Get next question_id
    existing_qs = interview.get("questions", [])
    max_qid = max(q.get("question_id", -1) for q in existing_qs)
    next_qid = max_qid + 1

    # ➕ Save new question to DB
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

    # 🚀 Start async processing tasks
    process_question_audio.delay(interview_id, max_qid, audio_bytes)
    generate_avatar_video.delay(interview_id, next_qid, new_question_text)
    process_question_video.delay(interview_id, max_qid, video_bytes)

    # ✅ Update last question to "processing"
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



from app.tasks import process_job_specific_cv

@app.post("/cv/match_specific")
async def analyze_job_specific_cv(
    user_id: str = Form(...),
    job_title: str = Form(...),
    governorate: str = Form(...),
    level: str = Form(...),
    file: UploadFile = File(...)
):
    cv_bytes = await file.read()
    process_job_specific_cv.delay(user_id, cv_bytes, file.filename, job_title, governorate, level)

    return {
        "message": "Job-specific CV analysis started.",
        "filename": file.filename,
        "job_title": job_title,
        "governorate": governorate,
        "level": level
    }

@app.get("/cv/match_specific/{user_id}")
def get_job_specific_cv(user_id: str):
    record = db["cv_job_match"].find_one({"user_id": user_id}, sort=[("created_at", -1)])
    if not record:
        raise HTTPException(status_code=404, detail="No job-specific CV record found.")

    record["_id"] = str(record["_id"])
    if "created_at" in record:
        record["created_at"] = record["created_at"].isoformat()

    return record






users_collection = db["users"]


@app.post("/signup")
def signup(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    # Check if user already exists
    if users_collection.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="Email already registered!")

    # Determine new user_id (incrementing manually)
    last_user = users_collection.find_one(sort=[("user_id", -1)])
    new_user_id = (last_user["user_id"] + 1) if last_user else 1

    user_data = {
        "user_id": new_user_id,
        "name": name,
        "email": email,
        "password": password,
        "created_at": datetime.utcnow()
    }

    users_collection.insert_one(user_data)
    return {"success": True, "message": "User registered successfully!", "user_id": new_user_id}


@app.post("/signin")
def signin(
    email: str = Form(...),
    password: str = Form(...)
):
    user = users_collection.find_one({"email": email})
    if not user or user["password"] != password:
        raise HTTPException(status_code=400, detail="Invalid credentials!")

    return {
        "success": True,
        "message": "Login successful",
        "data": {
            "user_id": user["user_id"],
            "name": user["name"],
            "email": user["email"]
        }
    }


@app.get("/users")
def get_all_users():
    users = list(users_collection.find({}, {"_id": 0}))
    return {"success": True, "users": users}
