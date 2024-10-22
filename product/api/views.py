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
from product.models import Product, Category, ProductCategory
from django.db import transaction


class MyCursorPagination(CursorPagination):
    page_size = 19
    ordering = "-product_id"  # `product_id` 필드를 기준으로 역순 정렬


class ProductViewSet(
    viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin
):
    serializer_class = ProductSerializer
    queryset = Product.objects.prefetch_related("categories").all()
    pagination_class = MyCursorPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ProductFilter
    ordering_fields = ['discount_rate', 'price', 'purchase_count']

    def get_queryset(self):
        queryset = super().get_queryset()

        # "random" 파라미터가 true로 설정된 경우 랜덤 상품 카테고리에서 상품을 반환
        random_param = self.request.query_params.get('random', 'false').lower()
        if random_param == 'true':
            random_category, created = Category.objects.get_or_create(name="오직 포캣")
            # 랜덤 상품 카테고리가 비어있으면 populate_random_category 실행
            if not random_category.products.exists():  # 여기서 products로 수정
                self.populate_random_category(random_category)
            return random_category.products.all()

        ordering = self.request.query_params.get('ordering', None)
        if ordering:
            queryset = queryset.order_by(ordering)
        return queryset

    def populate_random_category(self, random_category):
        # 카테고리에 이미 상품이 없을 때만 실행
        if not ProductCategory.objects.filter(category=random_category).exists():
            # 상품을 랜덤으로 19개 선택해서 카테고리에 추가
            random_products = Product.objects.order_by('?')[:19]

            with transaction.atomic():
                for product in random_products:
                    ProductCategory.objects.create(product=product, category=random_category)


class CategoryViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = CategoryListSerializer
    queryset = Category.objects.all()

    def list(self, request, *args, **kwargs):
        categories = Category.objects.filter(parent_category__isnull=True)
        serializer = CategoryListSerializer(categories, many=True)
        return Response(serializer.data)