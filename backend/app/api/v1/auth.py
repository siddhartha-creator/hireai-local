from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.dependencies import CurrentUserDependency, get_auth_service
from app.modules.auth.service import AuthService
from app.schemas.auth import TokenResponse, UserCreate, UserLogin, UserRead

router = APIRouter()


@router.get("/status")
async def auth_status() -> dict:
    return {"module": "auth", "status": "ready"}


@router.post("/register", response_model=UserRead, status_code=201)
async def register_user(
    payload: UserCreate,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    return auth_service.register(payload)


@router.post("/login", response_model=TokenResponse)
async def login_user(
    payload: UserLogin,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    return auth_service.login(payload)


@router.get("/me", response_model=UserRead)
async def read_auth_me(current_user: CurrentUserDependency):
    return current_user
