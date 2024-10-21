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
        price=Decimal("100.00"),
        discount_rate=Decimal("10.00"),
        purchase_count=5,
    )
    product_image = ProductImage.objects.create(image_url="https://url/test_image.jpg")
    product_image_2 = ProductImage.objects.create(
        image_url="https://url/test_image_2.jpg"
    )

    category_1 = Category.objects.create(name="category_1")
    category_2 = Category.objects.create(name="category_2", parent_category=category_1)

    product.description_images.add(product_image)
    product.description_images.add(product_image_2)

    ProductCategory.objects.create(product=product, category=category_1)
    ProductCategory.objects.create(product=product, category=category_2)


@pytest.fixture()
def 테스트_여러_상품_생성():
    # 카테고리 생성
    category_1 = Category.objects.create(name="category_1")
    category_2 = Category.objects.create(name="category_2", parent_category=category_1)
    category_3 = Category.objects.create(name="category_3")

    # 여러 상품 생성
    for i in range(1, 4):  # 3개의 상품 생성
        product = Product.objects.create(
            name=f"Test Product {i}",
            thumbnail_url=f"https://url/test_thumbnail_{i}.jpg",
            price=Decimal(f"{100 * i}.00"),
            discount_rate=Decimal(f"{5 * i}.00"),
            purchase_count=i * 5,
        )

        # 각 상품에 대한 이미지 생성
        for j in range(1, 3):  # 각 상품마다 2개의 이미지 생성
            product_image = ProductImage.objects.create(
                image_url=f"https://url/test_image_{i}_{j}.jpg"
            )
            product.description_images.add(product_image)

        # 카테고리 연결
        ProductCategory.objects.create(product=product, category=category_1)
        if i % 2 == 0:  # 짝수 번호의 상품은 두 번째 카테고리에도 연결
            ProductCategory.objects.create(product=product, category=category_2)
        elif i % 3 == 0:
            ProductCategory.objects.create(product=product, category=category_3)


@pytest.mark.django_db
class TestCase:
    def test_특정_상품_조회_테스트(self, api_client, 테스트_상품_생성):
        # product_id를 포함한 엔드포인트 URL 생성
        url = reverse("product-detail", kwargs={"pk": 1})

        # GET 요청으로 상품 조회
        response = api_client.get(url)

        # 응답 데이터가 잘 전달 되는지 확인
        assert response.json() == {
            "product_id": 1,
            "description_images": [
                {"image_url": "https://url/test_image.jpg"},
                {"image_url": "https://url/test_image_2.jpg"},
            ],
            "name": "Test Product",
            "thumbnail_url": "https://url/test_thumbnail.jpg",
            "price": "100.00",
            "discount_rate": "10.00",
            "purchase_count": 5,
            "categories": [{"name": "category_1"}, {"name": "category_2"}],
        }

    def test_모든_상품_조회_테스트(self, api_client, 테스트_여러_상품_생성):
        url = reverse("product-list")

        response = api_client.get(url)

        assert response.json() == {
            "next": None,
            "previous": None,
            "results": [
                {
                    "product_id": 3,
                    "description_images": [
                        {"image_url": "https://url/test_image_3_1.jpg"},
                        {"image_url": "https://url/test_image_3_2.jpg"},
                    ],
                    "categories": [{"name": "category_1"}, {"name": "category_3"}],
                    "name": "Test Product 3",
                    "thumbnail_url": "https://url/test_thumbnail_3.jpg",
                    "price": "300.00",
                    "discount_rate": "15.00",
                    "purchase_count": 15,
                },
                {
                    "product_id": 2,
                    "description_images": [
                        {"image_url": "https://url/test_image_2_1.jpg"},
                        {"image_url": "https://url/test_image_2_2.jpg"},
                    ],
                    "categories": [{"name": "category_1"}, {"name": "category_2"}],
                    "name": "Test Product 2",
                    "thumbnail_url": "https://url/test_thumbnail_2.jpg",
                    "price": "200.00",
                    "discount_rate": "10.00",
                    "purchase_count": 10,
                },
                {
                    "product_id": 1,
                    "description_images": [
                        {"image_url": "https://url/test_image_1_1.jpg"},
                        {"image_url": "https://url/test_image_1_2.jpg"},
                    ],
                    "categories": [{"name": "category_1"}],
                    "name": "Test Product 1",
                    "thumbnail_url": "https://url/test_thumbnail_1.jpg",
                    "price": "100.00",
                    "discount_rate": "5.00",
                    "purchase_count": 5,
                },
            ],
        }

    def test_모든_상품_조회_카테고리_필터링_테스트(
        self, api_client, 테스트_여러_상품_생성
    ):
        # with CaptureQueriesContext(connection) as ctx:
        url = reverse("product-list")

        response = api_client.get(url + "?categories=2&categories=3")

        assert response.json() == {
            "next": None,
            "previous": None,
            "results": [
                {
                    "product_id": 3,
                    "description_images": [
                        {"image_url": "https://url/test_image_3_1.jpg"},
                        {"image_url": "https://url/test_image_3_2.jpg"},
                    ],
                    "categories": [{"name": "category_1"}, {"name": "category_3"}],
                    "name": "Test Product 3",
                    "thumbnail_url": "https://url/test_thumbnail_3.jpg",
                    "price": "300.00",
                    "discount_rate": "15.00",
                    "purchase_count": 15,
                },
                {
                    "product_id": 2,
                    "description_images": [
                        {"image_url": "https://url/test_image_2_1.jpg"},
                        {"image_url": "https://url/test_image_2_2.jpg"},
                    ],
                    "categories": [{"name": "category_1"}, {"name": "category_2"}],
                    "name": "Test Product 2",
                    "thumbnail_url": "https://url/test_thumbnail_2.jpg",
                    "price": "200.00",
                    "discount_rate": "10.00",
                    "purchase_count": 10,
                },
            ],
        }

    def test_모든_상품_조회_이름_필터링_테스트(self, api_client, 테스트_여러_상품_생성):
        url = reverse("product-list")

        response = api_client.get(url + "?name=3")

        assert response.json() == {
            "next": None,
            "previous": None,
            "results": [
                {
                    "product_id": 3,
                    "description_images": [
                        {"image_url": "https://url/test_image_3_1.jpg"},
                        {"image_url": "https://url/test_image_3_2.jpg"},
                    ],
                    "categories": [{"name": "category_1"}, {"name": "category_3"}],
                    "name": "Test Product 3",
                    "thumbnail_url": "https://url/test_thumbnail_3.jpg",
                    "price": "300.00",
                    "discount_rate": "15.00",
                    "purchase_count": 15,
                }
            ],
        }
