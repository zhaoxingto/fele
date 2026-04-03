from typing import Generic, TypeVar

from pydantic import BaseModel


T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    code: str = "0000"
    msg: str = "ok"
    data: T


class MessagePayload(BaseModel):
    message: str
