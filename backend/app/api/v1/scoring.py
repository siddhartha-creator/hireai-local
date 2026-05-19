from fastapi import APIRouter


router = APIRouter()


@router.get("/status")
async def scoring_status() -> dict:
    return {"module": "scoring", "status": "placeholder"}
