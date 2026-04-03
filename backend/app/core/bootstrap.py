from __future__ import annotations

import re

from sqlalchemy import inspect, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal, create_platform_tables, create_tenant_schema, engine, ensure_columns, is_sqlite
from app.core.security import hash_password
import app.models  # noqa: F401
from app.models.tenant import Tenant, TenantMembership, User


SCHEMA_PREFIX = "tenant_"


def slugify_company_name(name: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return value or "company"


def to_schema_name(slug: str) -> str:
    normalized = re.sub(r"[^a-z0-9_]+", "_", slug.lower()).strip("_")
    return f"{SCHEMA_PREFIX}{normalized or 'company'}"


def ensure_super_admin(session: Session) -> User:
    user = session.scalar(select(User).where(User.email == settings.super_admin_email))
    if user:
        return user

    user = User(
        email=settings.super_admin_email,
        full_name=settings.super_admin_name,
        password_hash=hash_password(settings.super_admin_password),
        is_superuser=True,
        is_active=True,
    )
    session.add(user)
    session.flush()
    return user


def provision_tenant(
    session: Session,
    *,
    company_name: str,
    company_id: str,
    owner_email: str,
    owner_password: str,
    owner_full_name: str,
    slug: str | None = None,
) -> Tenant:
    tenant_slug = slug or slugify_company_name(company_name)
    schema_name = to_schema_name(tenant_slug)

    tenant = session.scalar(select(Tenant).where(Tenant.slug == tenant_slug))
    if tenant:
        return tenant

    owner = session.scalar(select(User).where(User.email == owner_email))
    if owner is None:
        owner = User(
            email=owner_email,
            full_name=owner_full_name,
            password_hash=hash_password(owner_password),
            is_superuser=False,
            is_active=True,
        )
        session.add(owner)
        session.flush()

    tenant = Tenant(
        name=company_name,
        company_id=company_id,
        slug=tenant_slug,
        schema_name=schema_name,
        is_active=True,
    )
    session.add(tenant)
    session.flush()

    session.add(
        TenantMembership(
            tenant_id=tenant.id,
            user_id=owner.id,
            role="owner",
            is_active=True,
        )
    )
    create_tenant_schema(schema_name)
    session.flush()
    return tenant


def initialize_database() -> None:
    create_platform_tables()
    _apply_platform_migrations()

    with SessionLocal.begin() as session:
        ensure_super_admin(session)
        ensure_demo_tenant(session)
        schema_names = [tenant.schema_name for tenant in session.scalars(select(Tenant)).all()]

    for schema_name in schema_names:
        create_tenant_schema(schema_name)
        _apply_tenant_migrations(schema_name)


def ensure_demo_tenant(session: Session) -> Tenant:
    tenant = session.scalar(select(Tenant).where(Tenant.slug == "acme-trading"))
    if tenant:
        return tenant

    return provision_tenant(
        session,
        company_name="Acme Trading",
        company_id="10001",
        owner_email="owner@acme.local",
        owner_password="Owner@123456",
        owner_full_name="Acme Owner",
        slug="acme-trading",
    )


def _apply_platform_migrations() -> None:
    with engine.begin() as connection:
        ensure_columns(
            connection,
            "tenants",
            {
                "legal_name": "VARCHAR(160)",
                "contact_name": "VARCHAR(80)",
                "phone": "VARCHAR(30)",
                "email": "VARCHAR(255)",
                "address": "VARCHAR(255)",
                "remark": "VARCHAR(500)",
                "subscription_plan": "VARCHAR(80)",
                "subscription_status": "VARCHAR(30)",
                "subscription_expires_at": "TIMESTAMP WITH TIME ZONE",
                "subscription_scope": "VARCHAR(500)",
                "sku_rule_mode": "VARCHAR(30)",
                "sku_rule_prefix": "VARCHAR(30)",
                "sku_rule_digits": "INTEGER",
                "sku_rule_next_number": "INTEGER",
                "barcode_rule_mode": "VARCHAR(30)",
                "barcode_rule_prefix": "VARCHAR(30)",
                "barcode_rule_digits": "INTEGER",
                "barcode_rule_next_number": "INTEGER",
            },
        )
        ensure_columns(
            connection,
            "auth_sessions",
            {
                "login_ip": "VARCHAR(64)",
            },
        )


def _apply_tenant_migrations(schema_name: str) -> None:
    with engine.begin() as connection:
        tenant_connection = connection.execution_options(
            schema_translate_map={"tenant": None if is_sqlite else schema_name}
        )
        schema = None if is_sqlite else schema_name
        inspector = inspect(tenant_connection)
        existing_tables = set(inspector.get_table_names(schema=schema))

        if "product_categories" not in existing_tables:
            create_tenant_schema(schema_name)
            inspector = inspect(tenant_connection)

        ensure_columns(
            tenant_connection,
            "customers",
            {
                "code": "VARCHAR(40)",
                "email": "VARCHAR(255)",
                "address": "VARCHAR(255)",
                "remark": "VARCHAR(500)",
                "is_active": "BOOLEAN NOT NULL DEFAULT 1",
            },
            schema=schema,
        )
        ensure_columns(
            tenant_connection,
            "suppliers",
            {
                "code": "VARCHAR(40)",
                "email": "VARCHAR(255)",
                "address": "VARCHAR(255)",
                "remark": "VARCHAR(500)",
                "is_active": "BOOLEAN NOT NULL DEFAULT 1",
            },
            schema=schema,
        )
        ensure_columns(
            tenant_connection,
            "products",
            {
                "barcode": "VARCHAR(64)",
                "category_id": "VARCHAR(36)",
                "specification": "VARCHAR(120)",
                "remark": "VARCHAR(500)",
                "is_active": "BOOLEAN NOT NULL DEFAULT 1",
            },
            schema=schema,
        )
