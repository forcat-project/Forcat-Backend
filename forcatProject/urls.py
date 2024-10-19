from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import routers
from rest_framework.permissions import AllowAny

from product.api.views import ProductViewSet

schema_view = get_schema_view(
   openapi.Info(
      title="Forcat API",
      default_version='v1',
      description="API description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@forcat.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[AllowAny],
)


router = routers.DefaultRouter(trailing_slash=False)
router.register(r'products', ProductViewSet)

urlpatterns = [
    path('api/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/', include(router.urls)),
]