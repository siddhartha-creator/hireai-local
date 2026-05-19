from fastapi import APIRouter


router = APIRouter()


@router.get("/status")
async def interviews_status() -> dict:
    return {"module": "interviews", "status": "placeholder"}
