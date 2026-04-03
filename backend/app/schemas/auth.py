from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field
import re


EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def validate_dev_email(value: object) -> str:
    if not isinstance(value, str):
        raise TypeError("email must be a string")

    normalized = value.strip()

    if not EMAIL_PATTERN.fullmatch(normalized):
        raise ValueError("value is not a valid email address")

    return normalized


EmailValue = Annotated[str, BeforeValidator(validate_dev_email)]


class LoginRequest(BaseModel):
    email: EmailValue
    password: str = Field(min_length=6, max_length=128)


class RegisterCompanyRequest(BaseModel):
    company_name: str = Field(min_length=2, max_length=120)
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailValue
    password: str = Field(min_length=6, max_length=128)


class TokenResponse(BaseModel):
    token: str
    refreshToken: str


class RefreshTokenRequest(BaseModel):
    refreshToken: str


class CurrentUserResponse(BaseModel):
    userId: str
    userName: str
    roles: list[str]
    buttons: list[str]
    tenantId: str | None = None
    companyId: str | None = None
    companyName: str | None = None


class RegisterCompanyResponse(BaseModel):
    companyId: str
    companyName: str
    adminEmail: str
