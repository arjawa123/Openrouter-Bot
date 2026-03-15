from fastapi import APIRouter
from app.schemas.common import HealthResponse

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="ok")

@router.get("/")
async def root():
    return {"status": "Bot backend is running"}
