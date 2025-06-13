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
def process_job_specific_cv(user_id: str, file_bytes: bytes, filename: str, job_title: str, governorate: str, level: str):
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info(f"[🧾] Processing CV for user={user_id}, job={job_title}, gov={governorate}, level={level}")

    client = MongoClient(MONGODB_URL)
    db = client["interview_db"]
    collection = db["cv_job_match"]

    try:
        file_stream = io.BytesIO(file_bytes)
        file_stream.name = filename

        response = requests.post(
            "http://10.100.102.6:8080/job_specific/inference",
            files={"file": file_stream},
            data={
                "job_title": job_title,
                "governorate": governorate,
                "level": level
            }
        )
        logger.info(f"[✅] Job model response status: {response.status_code}")
        data = response.json()
        logger.info(f"[📥] Model output: {data}")

        record = {
            "user_id": user_id,
            "cv_filename": filename,
            "job_title": job_title,
            "governorate": governorate,
            "level": level,
            "summary": data.get("summary", ""),
            "cv_skills_found": data.get("cv_skills_found", []),
            "matched_skills": data.get("matched_skills", {}),
            "missing_skills": data.get("missing_skills", {}),
            "top_missing_suggestions": data.get("top_missing_suggestions", []),
            "recommendation": data.get("recommendation", ""),
            "created_at": datetime.utcnow()
        }

        result = collection.insert_one(record)
        logger.info(f"[💾] Inserted Job-Specific CV record ID: {result.inserted_id}")

    except Exception as e:
        logger.error(f"❌ Job-Specific CV Error: {e}")
    finally:
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






@celery.task
def process_question_video(interview_id: str, question_id: int, video_bytes: bytes):
    import io
    import logging

    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger("face_video")

    log.info(f"🎬 [START] Processing video for Interview {interview_id}, QID {question_id}")

    client = MongoClient(MONGODB_URL)
    db = client["interview_db"]
    interviews_collection = db["interviews"]

    try:
        file_stream = io.BytesIO(video_bytes)
        file_stream.name = "video.mp4"

        log.info(f"📤 Sending video to Face Emotion API")
        response = requests.post(
            "http://10.100.102.6:4400/video/inference",
            files={"file": file_stream}
        )

        response.raise_for_status()
        face_emotion_data = response.json()

        log.info(f"✅ Got response: {face_emotion_data}")
        interviews_collection.update_one(
            {"_id": ObjectId(interview_id), "questions.question_id": question_id},
            {"$set": {"questions.$.face_emotion": face_emotion_data}}
        )

    except Exception as e:
        log.error(f"❌ Failed to process video: {str(e)}")
        interviews_collection.update_one(
            {"_id": ObjectId(interview_id), "questions.question_id": question_id},
            {"$set": {"questions.$.face_emotion": {"error": str(e)}}}
        )
    finally:
        client.close()
        log.info(f"✅ Finished face emotion processing for QID {question_id}")







print(f"✅ Registered Celery tasks: {celery.tasks.keys()}")
