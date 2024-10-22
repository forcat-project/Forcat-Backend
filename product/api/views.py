from urllib.parse import unquote

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins
from rest_framework.pagination import CursorPagination
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter

from product.api.filter import ProductFilter
from product.api.serializer import (
    ProductSerializer,
    CategoryListSerializer,
)
from product.models import Product, Category


class MyCursorPagination(CursorPagination):
    page_size = 12
    ordering = "-product_id"  # `product_id` 필드를 기준으로 역순 정렬


class ProductViewSet(
    viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin
):
    serializer_class = ProductSerializer
    queryset = Product.objects.prefetch_related("categories").all()
    pagination_class = MyCursorPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ProductFilter
    ordering_fields = ['discount_rate', 'price']

    def get_queryset(self):
        queryset = super().get_queryset()
        ordering = self.request.query_params.get('ordering', None)
        if ordering:
            queryset = queryset.order_by(ordering)
        return queryset


class CategoryViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = CategoryListSerializer
    queryset = Category.objects.all()

    def list(self, request, *args, **kwargs):
        categories = Category.objects.filter(parent_category__isnull=True)
        serializer = CategoryListSerializer(categories, many=True)
        return Response(serializer.data)