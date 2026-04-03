from __future__ import annotations

import random
import string
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_superuser, get_current_tenant, get_tenant_db
from app.core.database import get_db
from app.core.security import hash_password
from app.models.customer import Customer
from app.models.product import Product, ProductCategory
from app.models.session import AuthSession
from app.models.supplier import Supplier
from app.models.tenant import Tenant, TenantMembership, User
from app.schemas.common import ApiResponse
from app.schemas.company import (
    AdminAccountListItem,
    AdminAccountLoginHistoryItem,
    AdminAccountPasswordResetRequest,
    AdminAccountStatusUpdateRequest,
    AdminTenantDetailResponse,
    AdminTenantListItem,
    AdminTenantStatusUpdateRequest,
    AdminSubscriptionListItem,
    AdminSubscriptionUpdateRequest,
    CompanyProfileResponse,
    CompanyCodeRulesResponse,
    CompanyCodeRulesUpdateRequest,
    CompanyProfileUpdateRequest,
    CustomerCreateRequest,
    CustomerResponse,
    CustomerUpdateRequest,
    GenerateCodeRequest,
    GenerateCodeResponse,
    ProductCategoryCreateRequest,
    ProductCategoryResponse,
    ProductCategoryUpdateRequest,
    ProductCreateRequest,
    ProductResponse,
    ProductUpdateRequest,
    SupplierCreateRequest,
    SupplierResponse,
    SupplierUpdateRequest,
)


router = APIRouter()


def _rule_payload(prefix: str | None, digits: int | None, next_number: int | None):
    return {
        "prefix": prefix or "",
        "digits": digits or 6,
        "nextNumber": next_number or 1,
    }


def _format_sequence(prefix: str, digits: int, current_number: int) -> str:
    return f"{prefix}{current_number:0{digits}d}"


def _format_random(prefix: str, digits: int, *, numeric_only: bool) -> str:
    alphabet = string.digits if numeric_only else string.ascii_uppercase + string.digits
    tail = "".join(random.choice(alphabet) for _ in range(digits))
    return f"{prefix}{tail}"


def _format_date_random(prefix: str, digits: int) -> str:
    date_part = datetime.now().strftime("%Y%m%d")
    tail = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(digits))
    return f"{prefix}{date_part}{tail}"


def _code_exists(tenant_db: Session, kind: str, code: str) -> bool:
    field = Product.sku if kind == "sku" else Product.barcode
    return tenant_db.scalar(select(Product.id).where(field == code)) is not None


def _company_payload(tenant: Tenant) -> CompanyProfileResponse:
    return CompanyProfileResponse(
        tenantId=tenant.id,
        companyId=tenant.company_id,
        companyName=tenant.name,
        legalName=tenant.legal_name,
        contactName=tenant.contact_name,
        phone=tenant.phone,
        email=tenant.email,
        address=tenant.address,
        remark=tenant.remark,
    )


def _company_code_rules_payload(tenant: Tenant) -> CompanyCodeRulesResponse:
    return CompanyCodeRulesResponse(
        sku={
            "mode": tenant.sku_rule_mode or "sequence",
            **_rule_payload(tenant.sku_rule_prefix, tenant.sku_rule_digits, tenant.sku_rule_next_number),
        },
        barcode={
            "mode": tenant.barcode_rule_mode or "sequence",
            **_rule_payload(tenant.barcode_rule_prefix, tenant.barcode_rule_digits, tenant.barcode_rule_next_number),
        },
    )


def _customer_payload(customer: Customer) -> CustomerResponse:
    return CustomerResponse(
        id=customer.id,
        name=customer.name,
        code=customer.code,
        contactName=customer.contact_name,
        phone=customer.phone,
        email=customer.email,
        address=customer.address,
        remark=customer.remark,
        isActive=customer.is_active,
        createdAt=customer.created_at,
        updatedAt=customer.updated_at,
    )


def _supplier_payload(supplier: Supplier) -> SupplierResponse:
    return SupplierResponse(
        id=supplier.id,
        name=supplier.name,
        code=supplier.code,
        contactName=supplier.contact_name,
        phone=supplier.phone,
        email=supplier.email,
        address=supplier.address,
        remark=supplier.remark,
        isActive=supplier.is_active,
        createdAt=supplier.created_at,
        updatedAt=supplier.updated_at,
    )


def _category_payload(category: ProductCategory) -> ProductCategoryResponse:
    return ProductCategoryResponse(
        id=category.id,
        name=category.name,
        code=category.code,
        remark=category.remark,
        isActive=category.is_active,
        createdAt=category.created_at,
        updatedAt=category.updated_at,
    )


def _product_payload(product: Product, category_name: str | None = None) -> ProductResponse:
    return ProductResponse(
        id=product.id,
        sku=product.sku,
        barcode=product.barcode,
        name=product.name,
        categoryId=product.category_id,
        categoryName=category_name or (product.category.name if product.category else None),
        specification=product.specification,
        unit=product.unit,
        remark=product.remark,
        isActive=product.is_active,
        createdAt=product.created_at,
        updatedAt=product.updated_at,
    )


def _tenant_with_owner_query() -> Select[tuple[Tenant, User | None]]:
    owner_membership = (
        select(TenantMembership.tenant_id, TenantMembership.user_id)
        .where(TenantMembership.role == "owner", TenantMembership.is_active.is_(True))
        .subquery()
    )

    return (
        select(Tenant, User)
        .outerjoin(owner_membership, owner_membership.c.tenant_id == Tenant.id)
        .outerjoin(User, User.id == owner_membership.c.user_id)
        .order_by(Tenant.created_at.desc())
    )


def _admin_tenant_payload(tenant: Tenant, owner: User | None) -> AdminTenantListItem:
    return AdminTenantListItem(
        id=tenant.id,
        companyId=tenant.company_id,
        companyName=tenant.name,
        legalName=tenant.legal_name,
        contactName=tenant.contact_name,
        phone=tenant.phone,
        email=tenant.email,
        schemaName=tenant.schema_name,
        ownerName=owner.full_name if owner else None,
        ownerEmail=owner.email if owner else None,
        isActive=tenant.is_active,
        createdAt=tenant.created_at,
        updatedAt=tenant.updated_at,
    )


def _admin_tenant_detail_payload(tenant: Tenant, owner: User | None) -> AdminTenantDetailResponse:
    return AdminTenantDetailResponse(
        **_admin_tenant_payload(tenant, owner).model_dump(),
        address=tenant.address,
        remark=tenant.remark,
        subscriptionPlan=tenant.subscription_plan,
        subscriptionStatus=tenant.subscription_status,
        subscriptionExpiresAt=tenant.subscription_expires_at,
        subscriptionScope=tenant.subscription_scope,
    )


def _admin_subscription_payload(tenant: Tenant) -> AdminSubscriptionListItem:
    return AdminSubscriptionListItem(
        tenantId=tenant.id,
        companyId=tenant.company_id,
        companyName=tenant.name,
        subscriptionPlan=tenant.subscription_plan,
        subscriptionStatus=tenant.subscription_status,
        subscriptionExpiresAt=tenant.subscription_expires_at,
        subscriptionScope=tenant.subscription_scope,
        isActive=tenant.is_active,
        updatedAt=tenant.updated_at,
    )


@router.get("/admin/tenants", response_model=ApiResponse[list[AdminTenantListItem]])
def list_admin_tenants(
    _superuser: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
) -> ApiResponse[list[AdminTenantListItem]]:
    rows = db.execute(_tenant_with_owner_query()).all()
    return ApiResponse(data=[_admin_tenant_payload(tenant, owner) for tenant, owner in rows])


@router.get("/admin/tenants/{tenant_id}", response_model=ApiResponse[AdminTenantDetailResponse])
def get_admin_tenant_detail(
    tenant_id: str,
    _superuser: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
) -> ApiResponse[AdminTenantDetailResponse]:
    row = db.execute(_tenant_with_owner_query().where(Tenant.id == tenant_id)).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Tenant not found")

    tenant, owner = row
    return ApiResponse(data=_admin_tenant_detail_payload(tenant, owner))


@router.put("/admin/tenants/{tenant_id}/status", response_model=ApiResponse[AdminTenantListItem])
def update_admin_tenant_status(
    tenant_id: str,
    payload: AdminTenantStatusUpdateRequest,
    _superuser: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
) -> ApiResponse[AdminTenantListItem]:
    tenant = db.get(Tenant, tenant_id)
    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")

    tenant.is_active = payload.isActive
    db.commit()
    db.refresh(tenant)

    row = db.execute(_tenant_with_owner_query().where(Tenant.id == tenant_id)).first()
    owner = row[1] if row else None
    return ApiResponse(data=_admin_tenant_payload(tenant, owner))


@router.get("/admin/accounts", response_model=ApiResponse[list[AdminAccountListItem]])
def list_admin_accounts(
    _superuser: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
) -> ApiResponse[list[AdminAccountListItem]]:
    owner_membership = (
        select(TenantMembership.user_id, TenantMembership.tenant_id, TenantMembership.role)
        .where(TenantMembership.is_active.is_(True))
        .subquery()
    )

    rows = (
        db.execute(
            select(User, Tenant, owner_membership.c.role)
            .outerjoin(owner_membership, owner_membership.c.user_id == User.id)
            .outerjoin(Tenant, Tenant.id == owner_membership.c.tenant_id)
            .order_by(User.created_at.desc())
        )
        .all()
    )

    accounts = [
        AdminAccountListItem(
            id=user.id,
            fullName=user.full_name,
            email=user.email,
            accountType="platform" if user.is_superuser else "company_admin",
            tenantName=tenant.name if tenant else None,
            tenantId=tenant.id if tenant else None,
            tenantRole=role,
            isActive=user.is_active,
            createdAt=user.created_at,
            updatedAt=user.updated_at,
        )
        for user, tenant, role in rows
    ]
    return ApiResponse(data=accounts)


@router.put("/admin/accounts/{user_id}/status", response_model=ApiResponse[AdminAccountListItem])
def update_admin_account_status(
    user_id: str,
    payload: AdminAccountStatusUpdateRequest,
    current_superuser: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
) -> ApiResponse[AdminAccountListItem]:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == current_superuser.id and not payload.isActive:
        raise HTTPException(status_code=400, detail="Cannot disable current super admin")

    user.is_active = payload.isActive
    db.commit()
    db.refresh(user)

    row = (
        db.execute(
            select(Tenant, TenantMembership.role)
            .outerjoin(TenantMembership, TenantMembership.tenant_id == Tenant.id)
            .where(TenantMembership.user_id == user.id, TenantMembership.is_active.is_(True))
        )
        .first()
    )
    tenant = row[0] if row else None
    role = row[1] if row else None

    return ApiResponse(
        data=AdminAccountListItem(
            id=user.id,
            fullName=user.full_name,
            email=user.email,
            accountType="platform" if user.is_superuser else "company_admin",
            tenantName=tenant.name if tenant else None,
            tenantId=tenant.id if tenant else None,
            tenantRole=role,
            isActive=user.is_active,
            createdAt=user.created_at,
            updatedAt=user.updated_at,
        )
    )


@router.put("/admin/accounts/{user_id}/reset-password", response_model=ApiResponse[dict[str, str]])
def reset_admin_account_password(
    user_id: str,
    payload: AdminAccountPasswordResetRequest,
    _superuser: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
) -> ApiResponse[dict[str, str]]:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user.password_hash = hash_password(payload.newPassword)
    db.commit()
    return ApiResponse(data={"message": "Password reset successful"})


@router.get("/admin/accounts/{user_id}/login-history", response_model=ApiResponse[list[AdminAccountLoginHistoryItem]])
def get_admin_account_login_history(
    user_id: str,
    _superuser: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
) -> ApiResponse[list[AdminAccountLoginHistoryItem]]:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    sessions = db.scalars(
        select(AuthSession)
        .where(AuthSession.user_id == user_id)
        .order_by(AuthSession.created_at.desc())
        .limit(7)
    ).all()

    return ApiResponse(
        data=[
            AdminAccountLoginHistoryItem(
                id=session.id,
                loginAt=session.created_at,
                loginIp=session.login_ip,
            )
            for session in sessions
        ]
    )


@router.get("/admin/subscriptions", response_model=ApiResponse[list[AdminSubscriptionListItem]])
def list_admin_subscriptions(
    _superuser: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
) -> ApiResponse[list[AdminSubscriptionListItem]]:
    tenants = db.scalars(select(Tenant).order_by(Tenant.created_at.desc())).all()
    return ApiResponse(data=[_admin_subscription_payload(tenant) for tenant in tenants])


@router.put("/admin/subscriptions/{tenant_id}", response_model=ApiResponse[AdminSubscriptionListItem])
def update_admin_subscription(
    tenant_id: str,
    payload: AdminSubscriptionUpdateRequest,
    _superuser: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
) -> ApiResponse[AdminSubscriptionListItem]:
    tenant = db.get(Tenant, tenant_id)
    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")

    tenant.subscription_plan = payload.subscriptionPlan
    tenant.subscription_status = payload.subscriptionStatus
    tenant.subscription_expires_at = payload.subscriptionExpiresAt
    tenant.subscription_scope = payload.subscriptionScope
    db.commit()
    db.refresh(tenant)
    return ApiResponse(data=_admin_subscription_payload(tenant))


@router.get("/profile", response_model=ApiResponse[CompanyProfileResponse])
def get_company_profile(tenant: Tenant = Depends(get_current_tenant)) -> ApiResponse[CompanyProfileResponse]:
    return ApiResponse(data=_company_payload(tenant))


@router.get("/code-rules", response_model=ApiResponse[CompanyCodeRulesResponse])
def get_company_code_rules(tenant: Tenant = Depends(get_current_tenant)) -> ApiResponse[CompanyCodeRulesResponse]:
    return ApiResponse(data=_company_code_rules_payload(tenant))


@router.put("/code-rules", response_model=ApiResponse[CompanyCodeRulesResponse])
def update_company_code_rules(
    payload: CompanyCodeRulesUpdateRequest,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
) -> ApiResponse[CompanyCodeRulesResponse]:
    current = db.get(Tenant, tenant.id)
    if current is None:
        raise HTTPException(status_code=404, detail="Tenant not found")

    current.sku_rule_prefix = payload.sku.prefix
    current.sku_rule_mode = payload.sku.mode
    current.sku_rule_digits = payload.sku.digits
    current.sku_rule_next_number = payload.sku.nextNumber
    current.barcode_rule_mode = payload.barcode.mode
    current.barcode_rule_prefix = payload.barcode.prefix
    current.barcode_rule_digits = payload.barcode.digits
    current.barcode_rule_next_number = payload.barcode.nextNumber
    db.commit()
    db.refresh(current)
    return ApiResponse(data=_company_code_rules_payload(current))


@router.post("/code-rules/generate", response_model=ApiResponse[GenerateCodeResponse])
def generate_company_code(
    payload: GenerateCodeRequest,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
    tenant_db: Session = Depends(get_tenant_db),
) -> ApiResponse[GenerateCodeResponse]:
    current = db.get(Tenant, tenant.id)
    if current is None:
        raise HTTPException(status_code=404, detail="Tenant not found")

    kind = payload.kind.lower()
    if kind == "sku":
        mode = current.sku_rule_mode or "sequence"
        prefix = current.sku_rule_prefix or ""
        digits = current.sku_rule_digits or 6
        current_number = current.sku_rule_next_number or 1
        if mode == "sequence":
            while True:
                code = _format_sequence(prefix, digits, current_number)
                current_number += 1
                if not _code_exists(tenant_db, kind, code):
                    current.sku_rule_next_number = current_number
                    next_number = current_number
                    break
        elif mode == "random":
            for _ in range(50):
                code = _format_random(prefix, digits, numeric_only=False)
                if not _code_exists(tenant_db, kind, code):
                    next_number = current_number
                    break
            else:
                raise HTTPException(status_code=409, detail="Unable to generate unique SKU")
        elif mode == "date_random":
            for _ in range(50):
                code = _format_date_random(prefix, digits)
                if not _code_exists(tenant_db, kind, code):
                    next_number = current_number
                    break
            else:
                raise HTTPException(status_code=409, detail="Unable to generate unique SKU")
        else:
            raise HTTPException(status_code=400, detail="Unsupported SKU rule mode")
    elif kind == "barcode":
        mode = current.barcode_rule_mode or "sequence"
        prefix = current.barcode_rule_prefix or ""
        digits = current.barcode_rule_digits or 13
        current_number = current.barcode_rule_next_number or 1
        if mode == "sequence":
            while True:
                code = _format_sequence(prefix, digits, current_number)
                current_number += 1
                if not _code_exists(tenant_db, kind, code):
                    current.barcode_rule_next_number = current_number
                    next_number = current_number
                    break
        elif mode == "random":
            for _ in range(50):
                code = _format_random(prefix, digits, numeric_only=True)
                if not _code_exists(tenant_db, kind, code):
                    next_number = current_number
                    break
            else:
                raise HTTPException(status_code=409, detail="Unable to generate unique barcode")
        else:
            raise HTTPException(status_code=400, detail="Unsupported barcode rule mode")
    else:
        raise HTTPException(status_code=400, detail="Unsupported code kind")

    db.commit()
    return ApiResponse(data=GenerateCodeResponse(kind=kind, code=code, nextNumber=next_number))


@router.put("/profile", response_model=ApiResponse[CompanyProfileResponse])
def update_company_profile(
    payload: CompanyProfileUpdateRequest,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
) -> ApiResponse[CompanyProfileResponse]:
    current = db.get(Tenant, tenant.id)
    if current is None:
        raise HTTPException(status_code=404, detail="Tenant not found")

    current.name = payload.companyName
    current.legal_name = payload.legalName
    current.contact_name = payload.contactName
    current.phone = payload.phone
    current.email = payload.email
    current.address = payload.address
    current.remark = payload.remark
    db.commit()
    db.refresh(current)
    return ApiResponse(data=_company_payload(current))


@router.get("/customers", response_model=ApiResponse[list[CustomerResponse]])
def list_customers(db: Session = Depends(get_tenant_db)) -> ApiResponse[list[CustomerResponse]]:
    customers = db.scalars(select(Customer).order_by(Customer.created_at.desc())).all()
    return ApiResponse(data=[_customer_payload(item) for item in customers])


@router.post("/customers", response_model=ApiResponse[CustomerResponse])
def create_customer(
    payload: CustomerCreateRequest,
    db: Session = Depends(get_tenant_db),
) -> ApiResponse[CustomerResponse]:
    customer = Customer(
        name=payload.name,
        code=payload.code,
        contact_name=payload.contactName,
        phone=payload.phone,
        email=payload.email,
        address=payload.address,
        remark=payload.remark,
        is_active=payload.isActive,
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return ApiResponse(data=_customer_payload(customer))


@router.put("/customers/{customer_id}", response_model=ApiResponse[CustomerResponse])
def update_customer(
    customer_id: str,
    payload: CustomerUpdateRequest,
    db: Session = Depends(get_tenant_db),
) -> ApiResponse[CustomerResponse]:
    customer = db.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    customer.name = payload.name
    customer.code = payload.code
    customer.contact_name = payload.contactName
    customer.phone = payload.phone
    customer.email = payload.email
    customer.address = payload.address
    customer.remark = payload.remark
    customer.is_active = payload.isActive
    db.commit()
    db.refresh(customer)
    return ApiResponse(data=_customer_payload(customer))


@router.get("/suppliers", response_model=ApiResponse[list[SupplierResponse]])
def list_suppliers(db: Session = Depends(get_tenant_db)) -> ApiResponse[list[SupplierResponse]]:
    suppliers = db.scalars(select(Supplier).order_by(Supplier.created_at.desc())).all()
    return ApiResponse(data=[_supplier_payload(item) for item in suppliers])


@router.post("/suppliers", response_model=ApiResponse[SupplierResponse])
def create_supplier(
    payload: SupplierCreateRequest,
    db: Session = Depends(get_tenant_db),
) -> ApiResponse[SupplierResponse]:
    supplier = Supplier(
        name=payload.name,
        code=payload.code,
        contact_name=payload.contactName,
        phone=payload.phone,
        email=payload.email,
        address=payload.address,
        remark=payload.remark,
        is_active=payload.isActive,
    )
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return ApiResponse(data=_supplier_payload(supplier))


@router.put("/suppliers/{supplier_id}", response_model=ApiResponse[SupplierResponse])
def update_supplier(
    supplier_id: str,
    payload: SupplierUpdateRequest,
    db: Session = Depends(get_tenant_db),
) -> ApiResponse[SupplierResponse]:
    supplier = db.get(Supplier, supplier_id)
    if supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")

    supplier.name = payload.name
    supplier.code = payload.code
    supplier.contact_name = payload.contactName
    supplier.phone = payload.phone
    supplier.email = payload.email
    supplier.address = payload.address
    supplier.remark = payload.remark
    supplier.is_active = payload.isActive
    db.commit()
    db.refresh(supplier)
    return ApiResponse(data=_supplier_payload(supplier))


@router.get("/categories", response_model=ApiResponse[list[ProductCategoryResponse]])
def list_categories(db: Session = Depends(get_tenant_db)) -> ApiResponse[list[ProductCategoryResponse]]:
    categories = db.scalars(select(ProductCategory).order_by(ProductCategory.created_at.desc())).all()
    return ApiResponse(data=[_category_payload(item) for item in categories])


@router.post("/categories", response_model=ApiResponse[ProductCategoryResponse])
def create_category(
    payload: ProductCategoryCreateRequest,
    db: Session = Depends(get_tenant_db),
) -> ApiResponse[ProductCategoryResponse]:
    category = ProductCategory(
        name=payload.name,
        code=payload.code,
        remark=payload.remark,
        is_active=payload.isActive,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return ApiResponse(data=_category_payload(category))


@router.put("/categories/{category_id}", response_model=ApiResponse[ProductCategoryResponse])
def update_category(
    category_id: str,
    payload: ProductCategoryUpdateRequest,
    db: Session = Depends(get_tenant_db),
) -> ApiResponse[ProductCategoryResponse]:
    category = db.get(ProductCategory, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    category.name = payload.name
    category.code = payload.code
    category.remark = payload.remark
    category.is_active = payload.isActive
    db.commit()
    db.refresh(category)
    return ApiResponse(data=_category_payload(category))


@router.get("/products", response_model=ApiResponse[list[ProductResponse]])
def list_products(db: Session = Depends(get_tenant_db)) -> ApiResponse[list[ProductResponse]]:
    products = db.scalars(select(Product).order_by(Product.created_at.desc())).all()
    return ApiResponse(data=[_product_payload(item) for item in products])


@router.post("/products", response_model=ApiResponse[ProductResponse])
def create_product(
    payload: ProductCreateRequest,
    db: Session = Depends(get_tenant_db),
) -> ApiResponse[ProductResponse]:
    if payload.categoryId:
        category = db.get(ProductCategory, payload.categoryId)
        if category is None:
            raise HTTPException(status_code=404, detail="Category not found")

    product = Product(
        sku=payload.sku,
        barcode=payload.barcode,
        name=payload.name,
        category_id=payload.categoryId,
        specification=payload.specification,
        unit=payload.unit,
        remark=payload.remark,
        is_active=payload.isActive,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return ApiResponse(data=_product_payload(product))


@router.put("/products/{product_id}", response_model=ApiResponse[ProductResponse])
def update_product(
    product_id: str,
    payload: ProductUpdateRequest,
    db: Session = Depends(get_tenant_db),
) -> ApiResponse[ProductResponse]:
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    if payload.categoryId:
        category = db.get(ProductCategory, payload.categoryId)
        if category is None:
            raise HTTPException(status_code=404, detail="Category not found")

    product.sku = payload.sku
    product.barcode = payload.barcode
    product.name = payload.name
    product.category_id = payload.categoryId
    product.specification = payload.specification
    product.unit = payload.unit
    product.remark = payload.remark
    product.is_active = payload.isActive
    db.commit()
    db.refresh(product)
    return ApiResponse(data=_product_payload(product))
