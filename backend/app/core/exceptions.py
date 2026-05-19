from uuid import uuid4

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class HireAIError(Exception):
    status_code = status.HTTP_400_BAD_REQUEST
    code = "domain_error"

    def __init__(self, message: str = "Domain error", *, details: list[dict] | None = None) -> None:
        self.message = message
        self.details = details or []
        super().__init__(message)


class AuthenticationError(HireAIError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "authentication_error"


class PermissionDeniedError(HireAIError):
    status_code = status.HTTP_403_FORBIDDEN
    code = "permission_denied"


class ResourceNotFoundError(HireAIError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "not_found"


class ConflictError(HireAIError):
    status_code = status.HTTP_409_CONFLICT
    code = "conflict"


def error_response(message: str, *, request_id: str, errors: list[dict] | None = None) -> dict:
    return {
        "data": None,
        "message": message,
        "request_id": request_id,
        "errors": errors or [],
    }


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(HireAIError)
    async def handle_domain_error(request: Request, exc: HireAIError) -> JSONResponse:
        request_id = request.headers.get("X-Request-ID", str(uuid4()))
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response(
                exc.message,
                request_id=request_id,
                errors=exc.details or [{"code": exc.code}],
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        request_id = request.headers.get("X-Request-ID", str(uuid4()))
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response(
                "Validation failed",
                request_id=request_id,
                errors=[
                    {
                        "field": ".".join(str(part) for part in error["loc"]),
                        "code": error["type"],
                        "message": error["msg"],
                    }
                    for error in exc.errors()
                ],
            ),
        )
