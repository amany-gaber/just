from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from services.main import JobMatcher

router = APIRouter(
    prefix="/cv",
    tags=["CV Matching"]
)

job_matcher = JobMatcher()

@router.post("/inference")
async def match_cv(
    file: UploadFile = File(...),
    job_title: str = Form(...),
    governorate: str = Form(...),
    level: str = Form(...)
):
    if not file.filename.endswith((".pdf", ".docx", ".txt")):
        raise HTTPException(status_code=400, detail="Only PDF, DOCX, and TXT files are supported.")

    try:
        result = job_matcher.match_job(file, job_title, governorate, level)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))