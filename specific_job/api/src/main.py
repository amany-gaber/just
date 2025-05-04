from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from routes.user import router
import uvicorn
from config import settings

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the routes from src/routes/user.py
app.include_router(router)

@app.get("/")
def root():
    return {"message": "Click /docs to see the API documentation"}

@app.exception_handler(404)
def not_found_error(request, exc):
    return {"detail": "Page Not Found. Click /docs to see the API documentation"}

@app.exception_handler(Exception)
def handle_exception(request, exc):
    return {"message": f"Oops! {str(exc)}. Please try again!"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.DOMAIN,
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG_MODE if hasattr(settings, "DEBUG_MODE") else False,
    )