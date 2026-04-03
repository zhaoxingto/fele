from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import TenantBase, TimestampMixin, UuidPrimaryKeyMixin


class Warehouse(TenantBase, UuidPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "warehouses"
    __table_args__ = (UniqueConstraint("code", name="uq_warehouses_code"),)

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    inventories = relationship("Inventory", back_populates="warehouse", cascade="all, delete-orphan")
