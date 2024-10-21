import django_filters
from django_filters import filters

from product.models import Product, Category


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name="name", lookup_expr="icontains"
    )  # name LIKE 검색
    categories = filters.ModelMultipleChoiceFilter(
        queryset=Category.objects.all(), to_field_name="category_id"
    )

    class Meta:
        model = Product
        fields = ["name", "categories"]
