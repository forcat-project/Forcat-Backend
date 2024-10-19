from rest_framework import viewsets, mixins
from rest_framework.pagination import CursorPagination

from product.api.serializer import ProductSerializer
from product.models import Product


class MyCursorPagination(CursorPagination):
    page_size = 10
    ordering = "-product_id"  # `product_id` 필드를 기준으로 역순 정렬


class ProductViewSet(
    viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin
):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    pagination_class = MyCursorPagination
