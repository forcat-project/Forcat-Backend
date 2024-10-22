from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import routers
from rest_framework.permissions import AllowAny

from account.api.google_oauth_views import GoogleOauthViewSet
from account.api.kakao_oauth_views import KakaoOauthViewSet
from account.api.naver_oauth_views import NaverOauthViewSet
from product.api.views import ProductViewSet
from product.api.views import ProductViewSet, CategoryViewSet

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
    path("api/oauth/google", GoogleOauthViewSet.as_view(), name="google-oauth-login"),
    path("api/oauth/naver", NaverOauthViewSet.as_view(), name="naver-oauth-login"),
    path("api/", include(router.urls)),
]
