from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import TenantBase, TimestampMixin, UuidPrimaryKeyMixin


class Inventory(TenantBase, UuidPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "inventories"
    __table_args__ = (
        UniqueConstraint("product_id", "warehouse_id", name="uq_inventories_product_warehouse"),
    )

    product_id: Mapped[str] = mapped_column(
        ForeignKey("tenant.products.id", ondelete="CASCADE"), nullable=False, index=True
    )
    warehouse_id: Mapped[str] = mapped_column(
        ForeignKey("tenant.warehouses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    product = relationship("Product", back_populates="inventories")
    warehouse = relationship("Warehouse", back_populates="inventories")
