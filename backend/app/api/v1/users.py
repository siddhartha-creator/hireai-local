from fastapi import APIRouter

from app.core.dependencies import CurrentUserDependency
from app.schemas.auth import UserRead


router = APIRouter()


@router.get("/status")
async def users_status() -> dict:
    return {"module": "users", "status": "placeholder"}


@router.get("/me", response_model=UserRead)
async def read_users_me(current_user: CurrentUserDependency):
    return current_user
