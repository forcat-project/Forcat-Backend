from rest_framework import serializers
from payments.models import Order, ProductOrder


class ProductOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductOrder
        fields = [
            "product_name",
            "price",
            "quantity",
            "discount_rate",
            "product_id",
            "product_company",
            "product_image",
        ]


class OrderSerializer(serializers.ModelSerializer):
    products = ProductOrderSerializer(
        many=True, source="productorder_set"
    )  # Order와 연결된 ProductOrder 정보를 가져오기

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "payment",
            "order_date",
            "original_amount",
            "points_used",
            "total_amount",
            "user_name",
            "phone_number",
            "shipping_address",
            "shipping_address_detail",
            "shipping_memo",
            "payment_method",
            "shipping_status",
            "products",
            "status",
            "cancellation_date",
        ]
