from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class CompanyProfileResponse(BaseModel):
    tenantId: str
    companyId: str
    companyName: str
    legalName: str | None = None
    contactName: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    remark: str | None = None


class CompanyProfileUpdateRequest(BaseModel):
    companyName: str = Field(min_length=2, max_length=120)
    legalName: str | None = Field(default=None, max_length=160)
    contactName: str | None = Field(default=None, max_length=80)
    phone: str | None = Field(default=None, max_length=30)
    email: str | None = Field(default=None, max_length=255)
    address: str | None = Field(default=None, max_length=255)
    remark: str | None = Field(default=None, max_length=500)


class CodeRuleConfig(BaseModel):
    mode: str = Field(default="sequence", max_length=30)
    prefix: str | None = Field(default=None, max_length=30)
    digits: int = Field(default=6, ge=1, le=20)
    nextNumber: int = Field(default=1, ge=1, le=999999999)


class CompanyCodeRulesResponse(BaseModel):
    sku: CodeRuleConfig
    barcode: CodeRuleConfig


class CompanyCodeRulesUpdateRequest(BaseModel):
    sku: CodeRuleConfig
    barcode: CodeRuleConfig


class GenerateCodeRequest(BaseModel):
    kind: str


class GenerateCodeResponse(BaseModel):
    kind: str
    code: str
    nextNumber: int


class CustomerBasePayload(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    code: str | None = Field(default=None, max_length=40)
    contactName: str | None = Field(default=None, max_length=80)
    phone: str | None = Field(default=None, max_length=30)
    email: str | None = Field(default=None, max_length=255)
    address: str | None = Field(default=None, max_length=255)
    remark: str | None = Field(default=None, max_length=500)
    isActive: bool = True


class CustomerCreateRequest(CustomerBasePayload):
    pass


class CustomerUpdateRequest(CustomerBasePayload):
    pass


class CustomerResponse(CustomerBasePayload):
    id: str
    createdAt: datetime
    updatedAt: datetime


class SupplierBasePayload(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    code: str | None = Field(default=None, max_length=40)
    contactName: str | None = Field(default=None, max_length=80)
    phone: str | None = Field(default=None, max_length=30)
    email: str | None = Field(default=None, max_length=255)
    address: str | None = Field(default=None, max_length=255)
    remark: str | None = Field(default=None, max_length=500)
    isActive: bool = True


class SupplierCreateRequest(SupplierBasePayload):
    pass


class SupplierUpdateRequest(SupplierBasePayload):
    pass


class SupplierResponse(SupplierBasePayload):
    id: str
    createdAt: datetime
    updatedAt: datetime


class ProductCategoryBasePayload(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    code: str | None = Field(default=None, max_length=40)
    remark: str | None = Field(default=None, max_length=500)
    isActive: bool = True


class ProductCategoryCreateRequest(ProductCategoryBasePayload):
    pass


class ProductCategoryUpdateRequest(ProductCategoryBasePayload):
    pass


class ProductCategoryResponse(ProductCategoryBasePayload):
    id: str
    createdAt: datetime
    updatedAt: datetime


class ProductBasePayload(BaseModel):
    sku: str = Field(min_length=1, max_length=64)
    barcode: str | None = Field(default=None, max_length=64)
    name: str = Field(min_length=2, max_length=150)
    categoryId: str | None = None
    specification: str | None = Field(default=None, max_length=120)
    unit: str = Field(default="pcs", min_length=1, max_length=30)
    remark: str | None = Field(default=None, max_length=500)
    isActive: bool = True


class ProductCreateRequest(ProductBasePayload):
    pass


class ProductUpdateRequest(ProductBasePayload):
    pass


class ProductResponse(ProductBasePayload):
    id: str
    categoryName: str | None = None
    createdAt: datetime
    updatedAt: datetime


class AdminTenantListItem(BaseModel):
    id: str
    companyId: str
    companyName: str
    legalName: str | None = None
    contactName: str | None = None
    phone: str | None = None
    email: str | None = None
    schemaName: str
    ownerName: str | None = None
    ownerEmail: str | None = None
    isActive: bool
    createdAt: datetime
    updatedAt: datetime


class AdminTenantDetailResponse(AdminTenantListItem):
    address: str | None = None
    remark: str | None = None
    subscriptionPlan: str | None = None
    subscriptionStatus: str | None = None
    subscriptionExpiresAt: datetime | None = None
    subscriptionScope: str | None = None


class AdminTenantStatusUpdateRequest(BaseModel):
    isActive: bool


class AdminAccountListItem(BaseModel):
    id: str
    fullName: str
    email: str
    accountType: str
    tenantName: str | None = None
    tenantId: str | None = None
    tenantRole: str | None = None
    isActive: bool
    createdAt: datetime
    updatedAt: datetime


class AdminAccountStatusUpdateRequest(BaseModel):
    isActive: bool


class AdminAccountPasswordResetRequest(BaseModel):
    newPassword: str = Field(min_length=8, max_length=64)


class AdminAccountLoginHistoryItem(BaseModel):
    id: str
    loginAt: datetime
    loginIp: str | None = None


class AdminSubscriptionListItem(BaseModel):
    tenantId: str
    companyId: str
    companyName: str
    subscriptionPlan: str | None = None
    subscriptionStatus: str | None = None
    subscriptionExpiresAt: datetime | None = None
    subscriptionScope: str | None = None
    isActive: bool
    updatedAt: datetime


class AdminSubscriptionUpdateRequest(BaseModel):
    subscriptionPlan: str | None = Field(default=None, max_length=80)
    subscriptionStatus: str | None = Field(default=None, max_length=30)
    subscriptionExpiresAt: datetime | None = None
    subscriptionScope: str | None = Field(default=None, max_length=500)
