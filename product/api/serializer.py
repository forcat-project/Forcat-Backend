from rest_framework import serializers

from product.models import Product, Category, CartItem, Cart


class CategoryListSerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["category_id", "name", "subcategories"]

    def get_subcategories(self, obj):
        return CategorySerializer(obj.subcategories.all(), many=True).data


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["category_id", "name"]


class ProductSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    discounted_price = serializers.SerializerMethodField()

    def get_discounted_price(self, obj):
        return obj.discounted_price  # @property 필드에서 값을 가져옴

    class Meta:
        model = Product
        fields = "__all__"


class CartProductSerializer(serializers.ModelSerializer):
    discounted_price = serializers.SerializerMethodField()

    def get_discounted_price(self, obj):
        return obj.discounted_price  # @property 필드에서 값을 가져옴

    class Meta:
        model = Product
        fields = [
            "product_id",
            "discounted_price",
            "name",
            "thumbnail_url",
            "company",
            "price",
            "discount_rate",
        ]


class CartItemReadSerializer(serializers.ModelSerializer):
    product = CartProductSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ["product", "quantity"]


class CartItemCreateSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    class Meta:
        model = CartItem
        fields = ["product_id", "quantity"]

    def create(self, validated_data):
        user_id = self.context["user_id"]
        cart, _ = Cart.objects.get_or_create(user_id=user_id)
        cart_item = CartItem.objects.create(
            cart=cart,
            product_id=validated_data["product_id"],
            quantity=validated_data["quantity"],
        )
        return cart_item


class CartItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = CartItem
        fields = ["quantity"]
