from django.db import models
from decimal import Decimal


class Product(models.Model):
    product_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    thumbnail_url = models.URLField()
    company = models.CharField(max_length=255, null=True)
    description_image_url = models.URLField(null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0.00"), null=True
    )
    remain_count = models.PositiveIntegerField(default=0)
    purchase_count = models.PositiveIntegerField(default=0, null=True)
    categories = models.ManyToManyField(
        "Category", through="ProductCategory", related_name="products"
    )

    @property
    def discounted_price(self):
        return Decimal(self.price) - Decimal(self.discount_rate / Decimal("100.00"))

    def __str__(self):
        return self.name


class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    parent_category = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="subcategories",
    )
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class ProductCategory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["product", "category"], name="unique_product_category"
            )
        ]

    def __str__(self):
        return f"{self.product.name} in {self.category.name}"
