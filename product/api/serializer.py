from rest_framework import serializers

from product.models import Product, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["name"]


class ProductSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    discounted_price = serializers.SerializerMethodField()

    def get_discounted_price(self, obj):
        return obj.discounted_price  # @property 필드에서 값을 가져옴

    class Meta:
        model = Product
        fields = "__all__"
