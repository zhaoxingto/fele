from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, MetaData, Uuid, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


platform_metadata = MetaData()
tenant_metadata = MetaData(schema="tenant")


class PlatformBase(DeclarativeBase):
    metadata = platform_metadata


class TenantBase(DeclarativeBase):
    metadata = tenant_metadata


class UuidPrimaryKeyMixin:
    id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
