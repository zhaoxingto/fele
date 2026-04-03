from __future__ import annotations

from datetime import datetime, timezone

from fastapi import Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, engine, get_db, is_sqlite
from app.models.session import AuthSession
from app.models.tenant import Tenant, User


def _extract_bearer_token(authorization: str | None) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")

    return authorization.split(" ", 1)[1].strip()


def get_current_session(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> AuthSession:
    token = _extract_bearer_token(authorization)
    session = db.scalar(select(AuthSession).where(AuthSession.access_token == token, AuthSession.is_active.is_(True)))

    if session is None or session.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Unauthorized")

    return session


def get_current_user(
    auth_session: AuthSession = Depends(get_current_session),
    db: Session = Depends(get_db),
) -> User:
    user = db.scalar(select(User).where(User.id == auth_session.user_id, User.is_active.is_(True)))
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user


def get_current_superuser(user: User = Depends(get_current_user)) -> User:
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Forbidden")
    return user


def get_current_tenant(
    auth_session: AuthSession = Depends(get_current_session),
    db: Session = Depends(get_db),
) -> Tenant:
    if auth_session.tenant_id is None:
        raise HTTPException(status_code=400, detail="No tenant selected")

    tenant = db.scalar(select(Tenant).where(Tenant.id == auth_session.tenant_id, Tenant.is_active.is_(True)))
    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")

    return tenant


def get_tenant_db(tenant: Tenant = Depends(get_current_tenant)):
    if is_sqlite:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
        return

    connection = engine.connect().execution_options(schema_translate_map={"tenant": tenant.schema_name})
    db = Session(bind=connection, autoflush=False, autocommit=False)
    try:
        yield db
    finally:
        db.close()
        connection.close()
