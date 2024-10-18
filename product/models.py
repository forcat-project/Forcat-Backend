from django.db import models
from decimal import Decimal


class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    thumbnail = models.ImageField(upload_to='product_thumbnails/')
    description_images = models.ManyToManyField('ProductImage', related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    purchase_count = models.PositiveIntegerField(default=0)

    @property
    def discounted_price(self):
        return Decimal(self.price) - Decimal(self.discount_rate / Decimal('100.00'))

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    image = models.ImageField(upload_to='product_description_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image {self.id} for product"
