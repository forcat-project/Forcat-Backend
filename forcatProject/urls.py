from django.urls import include, path
from drf_yasg import openapi
from payments.api.views import order_detail, OrderViewSet
from drf_yasg.views import get_schema_view
from rest_framework import routers
from rest_framework.permissions import AllowAny
from payments.api.views import PaymentViewSet
from account.api.kakao_oauth_views import KakaoOauthViewSet
from product.api.views import CartItemViewSet
from account.api.views import (
    CatViewSet,
    FileUploadView,
    UserViewSet,
    PointViewSet,
    CatBreedViewSet,
)
from product.api.views import (
    ProductViewSet,
    CategoryViewSet,
)


# Swagger 설정
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

# 기본 라우터
main_router = routers.DefaultRouter(trailing_slash=False)
main_router.register("products", ProductViewSet)
main_router.register("categories", CategoryViewSet)
main_router.register("users", UserViewSet)
main_router.register("points", PointViewSet, basename="points")
main_router.register("payments", PaymentViewSet, basename="payments")
main_router.register("cat-breed", CatBreedViewSet, basename="cat-breed")

# 사용자별 리소스 라우트 (cats, cart)
user_resource_routes = [
    path(
        "users/<int:user_id>/",
        include(
            [
                # 장바구니 라우트
                path(
                    "cart",
                    include(
                        [
                            path(
                                "/products/<int:products_id>",
                                CartItemViewSet.as_view(
                                    {
                                        "patch": "partial_update",
                                        "put": "update",
                                        "delete": "destroy",
                                    }
                                ),
                                name="user-cart-item",
                            ),
                            path(
                                "/products",
                                CartItemViewSet.as_view(
                                    {
                                        "get": "list",
                                        "post": "create",
                                    }
                                ),
                                name="user-cart-items",
                            ),
                        ]
                    ),
                ),
                # 고양이 라우트
                path(
                    "cats",
                    include(
                        [
                            path(
                                "/<int:cat_id>",
                                CatViewSet.as_view(
                                    {
                                        "get": "retrieve",  # 특정 고양이 조회
                                        "put": "update",  # 고양이 정보 전체 수정
                                        "patch": "partial_update",  # 고양이 정보 부분 수정
                                        "delete": "destroy",  # 고양이 삭제
                                    }
                                ),
                                name="user-cat-detail",
                            ),
                            path(
                                "",
                                CatViewSet.as_view(
                                    {
                                        "get": "list",  # 사용자의 모든 고양이 조회
                                        "post": "create",  # 새 고양이 등록
                                    }
                                ),
                                name="user-cats",
                            ),
                        ]
                    ),
                ),
                path(
                    "orders/<str:order_id>",
                    order_detail,
                    name="order_detail",
                ),
                path(
                    "orders/",
                    OrderViewSet.as_view({"post": "create_order", "get": "list"}),
                    name="order",
                ),
            ]
        ),
    ),
]

# API URL 패턴
api_v1_patterns = [
    # API 문서
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    # OAuth 관련
    path("oauth/kakao", KakaoOauthViewSet.as_view(), name="kakao-oauth-login"),
    # 파일 업로드
    path("upload", FileUploadView.as_view(), name="file-upload"),
    # 라우터 포함
    path("", include(main_router.urls)),
    path("", include(user_resource_routes)),
]

# 최상위 URL 패턴
urlpatterns = [
    path("api/", include(api_v1_patterns)),
]
