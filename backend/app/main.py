from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.bootstrap import initialize_database
from app.core.config import settings
from app.schemas.common import ApiResponse
import app.models  # noqa: F401


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    version="0.1.0",
)

app.include_router(api_router, prefix=settings.api_prefix)


@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
    code = "8888" if exc.status_code == 401 else str(exc.status_code)
    return JSONResponse(
        status_code=200,
        content=ApiResponse(code=code, msg=str(exc.detail), data=None).model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
    message = exc.errors()[0].get("msg", "请求参数不合法")
    return JSONResponse(
        status_code=200,
        content=ApiResponse(code="4220", msg=message, data=None).model_dump(),
    )


@app.on_event("startup")
def on_startup() -> None:
    initialize_database()


@app.get("/", tags=["system"])
def root() -> dict[str, str]:
    return {"message": f"{settings.app_name} is running"}
