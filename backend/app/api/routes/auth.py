from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.tenant import User
from app.schemas.auth import (
    CurrentUserResponse,
    LoginRequest,
    RefreshTokenRequest,
    RegisterCompanyRequest,
    RegisterCompanyResponse,
    TokenResponse,
)
from app.schemas.common import ApiResponse
from app.services.auth_service import (
    AuthError,
    authenticate_user,
    build_user_info,
    create_session,
    refresh_session,
    register_company,
)

router = APIRouter()


@router.post("/login", response_model=ApiResponse[TokenResponse])
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)) -> ApiResponse[TokenResponse]:
    try:
        user = authenticate_user(db, payload.email, payload.password)
        user_info = build_user_info(db, user)
        auth_session = create_session(db, user=user, tenant_id=user_info["tenantId"], login_ip=request.client.host if request.client else None)
        db.commit()
        return ApiResponse(
            data=TokenResponse(token=auth_session.access_token, refreshToken=auth_session.refresh_token)
        )
    except AuthError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/getUserInfo", response_model=ApiResponse[CurrentUserResponse])
def get_user_info(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApiResponse[CurrentUserResponse]:
    return ApiResponse(data=CurrentUserResponse(**build_user_info(db, user)))


@router.post("/refreshToken", response_model=ApiResponse[TokenResponse])
def refresh_token(
    payload: RefreshTokenRequest,
    db: Session = Depends(get_db),
) -> ApiResponse[TokenResponse]:
    try:
        auth_session = refresh_session(db, payload.refreshToken)
        db.commit()
        return ApiResponse(
            data=TokenResponse(token=auth_session.access_token, refreshToken=auth_session.refresh_token)
        )
    except AuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


@router.post("/register-company", response_model=ApiResponse[RegisterCompanyResponse])
def register_company_route(
    payload: RegisterCompanyRequest,
    db: Session = Depends(get_db),
) -> ApiResponse[RegisterCompanyResponse]:
    try:
        tenant = register_company(
            db,
            company_name=payload.company_name,
            full_name=payload.full_name,
            email=payload.email,
            password=payload.password,
        )
        db.commit()
        return ApiResponse(
            data=RegisterCompanyResponse(
                companyId=tenant.company_id,
                companyName=tenant.name,
                adminEmail=payload.email,
            )
        )
    except AuthError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
