from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import TenantBase, TimestampMixin, UuidPrimaryKeyMixin


class Product(TenantBase, UuidPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "products"
    __table_args__ = (UniqueConstraint("sku", name="uq_products_sku"),)

    sku: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    barcode: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    category_id: Mapped[str | None] = mapped_column(
        ForeignKey("tenant.product_categories.id", ondelete="SET NULL"), nullable=True, index=True
    )
    specification: Mapped[str | None] = mapped_column(String(120), nullable=True)
    unit: Mapped[str] = mapped_column(String(30), default="pcs", nullable=False)
    remark: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    category = relationship("ProductCategory", back_populates="products")
    inventories = relationship("Inventory", back_populates="product", cascade="all, delete-orphan")


class ProductCategory(TenantBase, UuidPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "product_categories"

    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    code: Mapped[str | None] = mapped_column(String(40), nullable=True, index=True)
    remark: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    products = relationship("Product", back_populates="category")
