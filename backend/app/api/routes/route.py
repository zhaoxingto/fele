from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.tenant import User
from app.schemas.common import ApiResponse
from app.schemas.route import MenuRoute, RouteMeta, UserRouteResponse


router = APIRouter()


def get_constant_routes() -> list[MenuRoute]:
    return [
        MenuRoute(
            id="403",
            name="403",
            path="/403",
            component="layout.blank$view.403",
            meta=RouteMeta(title="403", i18nKey="route.403", constant=True, hideInMenu=True),
        ),
        MenuRoute(
            id="404",
            name="404",
            path="/404",
            component="layout.blank$view.404",
            meta=RouteMeta(title="404", i18nKey="route.404", constant=True, hideInMenu=True),
        ),
        MenuRoute(
            id="500",
            name="500",
            path="/500",
            component="layout.blank$view.500",
            meta=RouteMeta(title="500", i18nKey="route.500", constant=True, hideInMenu=True),
        ),
        MenuRoute(
            id="iframe-page",
            name="iframe-page",
            path="/iframe-page/:url",
            component="layout.base$view.iframe-page",
            props=True,
            meta=RouteMeta(title="iframe-page", i18nKey="route.iframe-page", constant=True, hideInMenu=True),
        ),
        MenuRoute(
            id="login",
            name="login",
            path="/login/:module(pwd-login|code-login|register|reset-pwd|bind-wechat)?",
            component="layout.blank$view.login",
            props=True,
            meta=RouteMeta(title="login", i18nKey="route.login", constant=True, hideInMenu=True),
        ),
    ]


def get_super_admin_routes() -> list[MenuRoute]:
    return [
        MenuRoute(
            id="admin",
            name="admin",
            path="/admin",
            component="layout.base",
            meta=RouteMeta(title="管理后台", icon="mdi:shield-crown-outline", order=9),
            children=[
                MenuRoute(
                    id="admin_company",
                    name="admin_company",
                    path="/admin/company",
                    component="view.admin_company",
                    meta=RouteMeta(title="公司管理", icon="mdi:domain", order=1),
                ),
                MenuRoute(
                    id="admin_account",
                    name="admin_account",
                    path="/admin/account",
                    component="view.admin_account",
                    meta=RouteMeta(title="账号管理", icon="mdi:account-cog-outline", order=2),
                ),
                MenuRoute(
                    id="admin_subscription",
                    name="admin_subscription",
                    path="/admin/subscription",
                    component="view.admin_subscription",
                    meta=RouteMeta(title="订阅管理", icon="mdi:credit-card-outline", order=3),
                ),
            ],
        )
    ]


def get_auth_routes(user: User) -> list[MenuRoute]:
    routes = [
        MenuRoute(
            id="home",
            name="home",
            path="/home",
            component="layout.base$view.home",
            meta=RouteMeta(title="首页", i18nKey="route.home", icon="mdi:home-variant-outline", order=1),
        ),
        MenuRoute(
            id="order",
            name="order",
            path="/order",
            component="layout.base$view.order",
            meta=RouteMeta(title="订单管理", icon="mdi:clipboard-text-outline", order=2),
        ),
        MenuRoute(
            id="purchase",
            name="purchase",
            path="/purchase",
            component="layout.base$view.purchase",
            meta=RouteMeta(title="采购管理", icon="mdi:truck-delivery-outline", order=3),
        ),
        MenuRoute(
            id="inventory",
            name="inventory",
            path="/inventory",
            component="layout.base$view.inventory_dashboard",
            meta=RouteMeta(title="库存管理", icon="mdi:warehouse", order=4),
        ),
        MenuRoute(
            id="finance",
            name="finance",
            path="/finance",
            component="layout.base$view.finance",
            meta=RouteMeta(title="财务管理", icon="mdi:cash-multiple", order=5),
        ),
        MenuRoute(
            id="print",
            name="print",
            path="/print",
            component="layout.base$view.print",
            meta=RouteMeta(title="打印管理", icon="mdi:printer-outline", order=6),
        ),
        MenuRoute(
            id="report",
            name="report",
            path="/report",
            component="layout.base$view.report",
            meta=RouteMeta(title="报表管理", icon="mdi:chart-box-outline", order=7),
        ),
        MenuRoute(
            id="company",
            name="company",
            path="/company",
            component="layout.base$view.company",
            meta=RouteMeta(title="公司管理", icon="mdi:domain", order=8),
        ),
    ]

    if user.is_superuser:
        routes.extend(get_super_admin_routes())

    return routes


@router.get("/getConstantRoutes", response_model=ApiResponse[list[MenuRoute]])
def get_constant_routes_api() -> ApiResponse[list[MenuRoute]]:
    return ApiResponse(data=get_constant_routes())


@router.get("/getUserRoutes", response_model=ApiResponse[UserRouteResponse])
def get_user_routes_api(user: User = Depends(get_current_user)) -> ApiResponse[UserRouteResponse]:
    return ApiResponse(data=UserRouteResponse(routes=get_auth_routes(user), home="home"))


@router.get("/isRouteExist", response_model=ApiResponse[bool])
def is_route_exist(routeName: str, user: User = Depends(get_current_user)) -> ApiResponse[bool]:
    route_names: set[str] = set()

    def collect_names(routes: list[MenuRoute]) -> None:
        for route in routes:
            route_names.add(route.name)
            if route.children:
                collect_names(route.children)

    collect_names([*get_constant_routes(), *get_auth_routes(user)])
    return ApiResponse(data=routeName in route_names)
