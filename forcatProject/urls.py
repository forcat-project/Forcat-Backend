from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import routers
from rest_framework.permissions import AllowAny

from account.api.kakao_oauth_views import KakaoOauthViewSet
from product.api.views import (
    ProductViewSet,
    CategoryViewSet,
    CartItemViewSet,
)

schema_view = get_schema_view(
    openapi.Info(
        title="Forcat API",
        default_version="v1",
        description="API description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@forcat.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[AllowAny],
)


router = routers.DefaultRouter(trailing_slash=False)
router.register(r"products", ProductViewSet)
router.register(r"categories", CategoryViewSet)


urlpatterns = [
    path(
        "api/swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("api/oauth/kakao", KakaoOauthViewSet.as_view(), name="kakao-oauth-login"),
    path(
        "api/users/<int:user_id>/cart/products/<int:products_id>",
        CartItemViewSet.as_view(
            {
                "patch": "partial_update",  # 장바구니 아이템 수정 (부분 업데이트)
                "put": "update",  # 장바구니 아이템 수정 (전체 업데이트)
                "delete": "destroy",  # 장바구니 아이템 삭제
            }
        ),
        name="user-cart-item",
    ),
    path(
        "api/users/<int:user_id>/cart/products",
        CartItemViewSet.as_view(
            {
                "get": "list",  # 장바구니 아이템 목록 조회
                "post": "create",  # 장바구니 아이템 추가
            }
        ),
        name="user-cart-items",
    ),
    path("api/", include(router.urls)),
]
