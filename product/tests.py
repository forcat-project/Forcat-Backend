from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from product.models import Product, ProductImage, Category, ProductCategory


@pytest.fixture(scope="session")
def api_client():
    return APIClient()


@pytest.fixture()
def 테스트_상품_생성():
    product = Product.objects.create(
        name="Test Product",
        thumbnail_url="https://url/test_thumbnail.jpg",
        price=Decimal('100.00'),
        discount_rate=Decimal('10.00'),
        purchase_count=5
    )
    product_image = ProductImage.objects.create(image_url="https://url/test_image.jpg")
    product_image_2 = ProductImage.objects.create(image_url="https://url/test_image_2.jpg")

    category_1 = Category.objects.create(name="category_1")
    category_2 = Category.objects.create(name="category_2", parent_category=category_1)

    product.description_images.add(product_image)
    product.description_images.add(product_image_2)

    ProductCategory.objects.create(product=product, category=category_1)
    ProductCategory.objects.create(product=product, category=category_2)


@pytest.mark.django_db
class TestCase:
    def test_특정_상품_조회_테스트(self, api_client, 테스트_상품_생성):
        # product_id를 포함한 엔드포인트 URL 생성
        url = reverse('product-detail', kwargs={'pk': 1})

        # GET 요청으로 상품 조회
        response = api_client.get(url)

        # 응답 데이터가 잘 전달 되는지 확인
        assert response.json() == {
            'product_id': 1,
            'description_images': [
                {'image_url': 'https://url/test_image.jpg'},
                {'image_url': 'https://url/test_image_2.jpg'}
            ],
            'name': 'Test Product',
            'thumbnail_url': 'https://url/test_thumbnail.jpg',
            'price': '100.00',
            'discount_rate': '10.00',
            'purchase_count': 5,
            'categories': [
                {'name': 'category_1'},
                {'name': 'category_2'}
            ]
        }

    def test_모든_상품_조회_테스트(self, api_client, 테스트_상품_생성):
        ...
