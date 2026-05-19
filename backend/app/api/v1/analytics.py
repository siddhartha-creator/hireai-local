from fastapi import APIRouter


router = APIRouter()


@router.get("/status")
async def analytics_status() -> dict:
    return {"module": "analytics", "status": "placeholder"}
