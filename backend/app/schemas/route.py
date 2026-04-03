from __future__ import annotations

from pydantic import BaseModel, Field


class RouteMeta(BaseModel):
    title: str
    icon: str | None = None
    i18nKey: str | None = None
    constant: bool | None = None
    hideInMenu: bool | None = None
    keepAlive: bool | None = None
    order: int | None = None


class MenuRoute(BaseModel):
    id: str
    name: str
    path: str
    component: str
    meta: RouteMeta
    props: bool | None = None
    redirect: str | dict | None = None
    children: list["MenuRoute"] = Field(default_factory=list)


class UserRouteResponse(BaseModel):
    routes: list[MenuRoute]
    home: str


MenuRoute.model_rebuild()
