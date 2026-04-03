from __future__ import annotations

from datetime import datetime, timedelta, timezone
import random
import secrets

from sqlalchemy import Select, or_, select
from sqlalchemy.orm import Session

from app.core.bootstrap import provision_tenant
from app.core.security import hash_password, verify_password
from app.models.session import AuthSession
from app.models.tenant import Tenant, TenantMembership, User


ACCESS_TOKEN_HOURS = 8
REFRESH_TOKEN_DAYS = 30


class AuthError(Exception):
    pass


def _active_user_query() -> Select[tuple[User]]:
    return select(User).where(User.is_active.is_(True))


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = db.scalar(_active_user_query().where(User.email == email))
    if user is None or not verify_password(password, user.password_hash):
        raise AuthError("账号或密码错误")
    return user


def create_session(db: Session, *, user: User, tenant_id: str | None, login_ip: str | None = None) -> AuthSession:
    now = datetime.now(timezone.utc)
    auth_session = AuthSession(
        user_id=user.id,
        tenant_id=tenant_id,
        access_token=secrets.token_urlsafe(32),
        refresh_token=secrets.token_urlsafe(48),
        login_ip=login_ip,
        expires_at=now + timedelta(hours=ACCESS_TOKEN_HOURS),
        refresh_expires_at=now + timedelta(days=REFRESH_TOKEN_DAYS),
        is_active=True,
    )
    db.add(auth_session)
    db.flush()
    return auth_session


def refresh_session(db: Session, refresh_token: str) -> AuthSession:
    auth_session = db.scalar(
        select(AuthSession).where(AuthSession.refresh_token == refresh_token, AuthSession.is_active.is_(True))
    )
    if auth_session is None or auth_session.refresh_expires_at <= datetime.now(timezone.utc):
        raise AuthError("登录已过期，请重新登录")

    auth_session.access_token = secrets.token_urlsafe(32)
    auth_session.refresh_token = secrets.token_urlsafe(48)
    auth_session.expires_at = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_HOURS)
    auth_session.refresh_expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_DAYS)
    db.flush()
    return auth_session


def generate_company_id(db: Session) -> str:
    while True:
        company_id = f"{random.randint(0, 99999):05d}"
        exists = db.scalar(select(Tenant.id).where(Tenant.company_id == company_id))
        if not exists:
            return company_id


def register_company(
    db: Session,
    *,
    company_name: str,
    full_name: str,
    email: str,
    password: str,
) -> Tenant:
    existing_user = db.scalar(select(User.id).where(User.email == email))
    if existing_user:
        raise AuthError("该邮箱已注册")

    company_id = generate_company_id(db)
    tenant = provision_tenant(
        db,
        company_name=company_name,
        company_id=company_id,
        owner_email=email,
        owner_password=password,
        owner_full_name=full_name,
    )
    db.flush()
    return tenant


def get_user_membership(db: Session, *, user_id: str) -> TenantMembership | None:
    return db.scalar(
        select(TenantMembership)
        .where(TenantMembership.user_id == user_id, TenantMembership.is_active.is_(True))
        .order_by(TenantMembership.created_at.asc())
    )


def build_user_info(db: Session, user: User) -> dict:
    membership = get_user_membership(db, user_id=user.id)
    tenant = None
    roles: list[str] = []

    if user.is_superuser:
        roles.append("R_SUPER")

    if membership is not None:
        tenant = db.scalar(select(Tenant).where(Tenant.id == membership.tenant_id))
        roles.append(f"TENANT_{membership.role.upper()}")

    return {
        "userId": user.id,
        "userName": user.full_name,
        "roles": roles,
        "buttons": [],
        "tenantId": tenant.id if tenant else None,
        "companyId": tenant.company_id if tenant else None,
        "companyName": tenant.name if tenant else None,
    }
