import time

from django_filters.rest_framework import DjangoFilterBackend
from django_redis import get_redis_connection
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.pagination import CursorPagination
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter

from product.api.filter import ProductFilter
from product.api.serializer import (
    ProductSerializer,
    CategoryListSerializer,
    CategorySerializer,
    CartItemReadSerializer,
    CartItemCreateSerializer,
    CartItemSerializer,
)
from product.models import Product, Category, CartItem, Cart


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
    ordering_fields = ["discount_rate", "price", "purchase_count"]

    def get_queryset(self):
        queryset = super().get_queryset()

        # discount_rate로 정렬을 요구할때만 0보다 큰 값 필터 적용
        ordering = self.request.query_params.get("ordering", None)
        if ordering == "discount_rate" or ordering == "-discount_rate":
            queryset = queryset.filter(discount_rate__gt=0)
        if ordering:
            queryset = queryset.order_by(ordering)
        return queryset

    def list(self, request, *args, **kwargs):
        # Redis 연결 설정
        redis_conn = get_redis_connection("default")

        # 'name' 필터가 요청에 포함된 경우 Redis 카운트 증가
        name_filter = request.query_params.get("name")
        if name_filter:
            # 필터링된 검색어로 카운트를 증가시킴
            redis_conn.zincrby("product_search_count", 1, name_filter)

        return super().list(request, *args, **kwargs)

    @action(methods=["GET"], detail=False, url_path="popular-keywords")
    def popular_keywords(self, request):
        redis_conn = get_redis_connection("default")

        product_scores = {}
        for keyword, score in redis_conn.zrange(
            "product_search_count", 0, -1, withscores=True
        ):
            product_scores[keyword] = score
        # 검색 카운트 기준으로 정렬하여 상위 상품 반환
        top_keywords = sorted(product_scores.items(), key=lambda x: x[1], reverse=True)

        return Response(
            {
                "product_ids": [
                    {keyword[0].decode("utf-8"): keyword[1]}
                    for keyword in top_keywords[:10]
                ]
            }
        )


class CategoryViewSet(
    viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin
):
    serializer_class = CategoryListSerializer
    queryset = Category.objects.all()

    def list(self, request, *args, **kwargs):
        categories = Category.objects.filter(parent_category__isnull=True)
        serializer = CategoryListSerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = CategorySerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CartItemViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        user_id = self.kwargs.get("user_id")
        return CartItem.objects.filter(cart__user__id=user_id).select_related("product")

    def get_serializer_class(self):
        if self.action == "create":
            return CartItemCreateSerializer
        elif self.action in ["partial_update", "delete"]:
            return CartItemSerializer
        return CartItemReadSerializer

    def create(self, request, *args, **kwargs):
        user_id = self.kwargs.get("user_id")
        cart, _ = Cart.objects.get_or_create(user_id=user_id)

        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity")

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product_id=product_id, defaults={"quantity": quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return Response(
            CartItemReadSerializer(cart_item).data, status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        user_id = self.kwargs.get("user_id")
        product_id = self.kwargs.get("products_id")

        cart, _ = Cart.objects.get_or_create(user_id=user_id)
        cart_item = CartItem.objects.get(cart_id=cart.id, product_id=product_id)

        serializer = self.get_serializer(
            instance=cart_item,
            data={
                "quantity": request.data["quantity"],
            },
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        user_id = self.kwargs.get("user_id")
        product_id = self.kwargs.get("products_id")

        # 해당 user_id의 장바구니에서 product_id에 해당하는 상품을 찾음
        try:
            cart, _ = Cart.objects.get_or_create(user_id=user_id)
            cart_item = CartItem.objects.get(cart_id=cart.id, product_id=product_id)
            cart_item.delete()  # 장바구니 아이템 삭제
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response(
                {"error": "해당 상품이 장바구니에 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
