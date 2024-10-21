from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins
from rest_framework.pagination import CursorPagination

from product.api.filter import ProductFilter
from product.api.serializer import ProductSerializer
from product.models import Product


class MyCursorPagination(CursorPagination):
    page_size = 10
    ordering = "-product_id"  # `product_id` 필드를 기준으로 역순 정렬


class ProductViewSet(
    viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin
):
    serializer_class = ProductSerializer
    queryset = Product.objects.prefetch_related("categories").all()
    pagination_class = MyCursorPagination
    filter_backends = [DjangoFilterBackend]  # 필터 백엔드 활성화
    filterset_class = ProductFilter  # 필터셋 지정
