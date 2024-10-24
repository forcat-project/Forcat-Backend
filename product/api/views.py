from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins, status
from rest_framework.pagination import CursorPagination
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter

from account.models import User
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
        ordering = self.request.query_params.get("ordering", None)
        if ordering:
            queryset = queryset.order_by(ordering)
        return queryset


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
        serializer = self.get_serializer(
            data=request.data, context={"user_id": user_id}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        user_id = self.kwargs.get("user_id")
        product_id = self.kwargs.get("products_id")

        cart = Cart.objects.get(user_id=user_id)
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
            cart = Cart.objects.get(user_id=user_id)
            cart_item = CartItem.objects.get(cart_id=cart.id, product_id=product_id)
            cart_item.delete()  # 장바구니 아이템 삭제
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response(
                {"error": "해당 상품이 장바구니에 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
