from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import PlatformBase, TimestampMixin, UuidPrimaryKeyMixin


class Tenant(PlatformBase, UuidPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "tenants"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    company_id: Mapped[str] = mapped_column(String(5), unique=True, nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    schema_name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    legal_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    contact_name: Mapped[str | None] = mapped_column(String(80), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    remark: Mapped[str | None] = mapped_column(String(500), nullable=True)
    subscription_plan: Mapped[str | None] = mapped_column(String(80), nullable=True)
    subscription_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    subscription_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    subscription_scope: Mapped[str | None] = mapped_column(String(500), nullable=True)
    sku_rule_mode: Mapped[str | None] = mapped_column(String(30), nullable=True)
    sku_rule_prefix: Mapped[str | None] = mapped_column(String(30), nullable=True)
    sku_rule_digits: Mapped[int | None] = mapped_column(nullable=True)
    sku_rule_next_number: Mapped[int | None] = mapped_column(nullable=True)
    barcode_rule_mode: Mapped[str | None] = mapped_column(String(30), nullable=True)
    barcode_rule_prefix: Mapped[str | None] = mapped_column(String(30), nullable=True)
    barcode_rule_digits: Mapped[int | None] = mapped_column(nullable=True)
    barcode_rule_next_number: Mapped[int | None] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    memberships = relationship("TenantMembership", back_populates="tenant", cascade="all, delete-orphan")


class User(PlatformBase, UuidPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    memberships = relationship("TenantMembership", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("AuthSession", back_populates="user", cascade="all, delete-orphan")


class TenantMembership(PlatformBase, UuidPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "tenant_memberships"
    __table_args__ = (
        Index("ix_tenant_memberships_tenant_user", "tenant_id", "user_id", unique=True),
    )

    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[str] = mapped_column(String(30), nullable=False, default="staff")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    tenant = relationship("Tenant", back_populates="memberships")
    user = relationship("User", back_populates="memberships")
