from fastapi import APIRouter, UploadFile, File, HTTPException
from services import CVMatcher

router = APIRouter(
    prefix="/cv",
    tags=["CV Matching"]
)

cv_matcher = CVMatcher()

@router.post("/inference")
async def match_cv(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        file_bytes = await file.read()
        result = cv_matcher.run_inference(file_bytes)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
