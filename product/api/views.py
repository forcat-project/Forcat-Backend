from rest_framework import viewsets, mixins

from product.api.serializer import ProductSerializer
from product.models import Product


class ProductViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
