from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from product.models import Product, ProductImage


@pytest.fixture(scope="session")
def api_client():
    return APIClient()


@pytest.fixture()
def 테스트_상품_생성():
    product = Product.objects.create(
        name="Test Product",
        thumbnail="test_thumbnail.jpg",
        price=Decimal('100.00'),
        discount_rate=Decimal('10.00'),
        purchase_count=5
    )
    product_image = ProductImage.objects.create(image="test_image.jpg")
    product_image_2 = ProductImage.objects.create(image="test_image_2.jpg")
    product.description_images.add(product_image)
    product.description_images.add(product_image_2)


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
                {'image': 'http://testserver/test_image.jpg'},
                {'image': 'http://testserver/test_image_2.jpg'}
            ],
            'name': 'Test Product',
            'thumbnail': 'http://testserver/test_thumbnail.jpg',
            'price': '100.00',
            'discount_rate': '10.00',
            'purchase_count': 5
        }

    def test_모든_상품_조회_테스트(self, api_client, 테스트_상품_생성):
        ...
