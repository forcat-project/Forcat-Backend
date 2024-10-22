from base64 import b64decode
from decimal import Decimal
from urllib import parse

import pytest
from django.urls import reverse
from rest_framework.pagination import _positive_int
from rest_framework.test import APIClient
from product.models import Product, Category, ProductCategory


@pytest.fixture(scope="session")
def api_client():
    return APIClient()


@pytest.fixture()
def 테스트_상품_생성():
    product = Product.objects.create(
        product_id=1,
        name="Test Product",
        company="ohYes",
        thumbnail_url="https://url/test_thumbnail.jpg",
        description_image_url="https://url/test_image.jpg",
        price=Decimal("100.00"),
        discount_rate=Decimal("10.00"),
        purchase_count=5,
    )

    category_1 = Category.objects.create(name="category_1")
    category_2 = Category.objects.create(name="category_2", parent_category=category_1)

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
            product_id=i,
            name=f"Test Product {i}",
            company="ohYes",
            thumbnail_url=f"https://url/test_thumbnail_{i}.jpg",
            description_image_url=f"https://url/test_image_{i}.jpg",
            price=Decimal(f"{100 * i}.00"),
            discount_rate=Decimal(f"{5 * i}.00"),
            purchase_count=i * 5,
        )

        # 카테고리 연결
        ProductCategory.objects.create(product=product, category=category_1)
        if i % 2 == 0:  # 짝수 번호의 상품은 두 번째 카테고리에도 연결
            ProductCategory.objects.create(product=product, category=category_2)
        elif i % 3 == 0:
            ProductCategory.objects.create(product=product, category=category_3)


@pytest.fixture()
def 테스트_대량_상품_생성():
    # 카테고리 생성
    category_1 = Category.objects.create(name="category_1")
    category_2 = Category.objects.create(name="category_2", parent_category=category_1)
    category_3 = Category.objects.create(name="category_3")

    # 여러 상품 생성
    for i in range(1, 20):  # 19개의 상품 생성
        product = Product.objects.create(
            product_id=i,
            name=f"Test Product {i}",
            company="ohYes",
            thumbnail_url=f"https://url/test_thumbnail_{i}.jpg",
            description_image_url=f"https://url/test_image_{i}.jpg",
            price=Decimal(f"{100 * i}.00"),
            discount_rate=Decimal(f"{5 * i}.00"),
            purchase_count=i * 5,
        )

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
            "description_image_url": "https://url/test_image.jpg",
            "name": "Test Product",
            "company": "ohYes",
            "thumbnail_url": "https://url/test_thumbnail.jpg",
            "price": "100.00",
            "discount_rate": "10.00",
            "discounted_price": 90.0,
            "remain_count": 0,
            "purchase_count": 5,
            "categories": [
                {"category_id": 1, "name": "category_1"},
                {"category_id": 2, "name": "category_2"},
            ],
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
                    "description_image_url": "https://url/test_image_3.jpg",
                    "categories": [
                        {"category_id": 1, "name": "category_1"},
                        {"category_id": 3, "name": "category_3"},
                    ],
                    "name": "Test Product 3",
                    "company": "ohYes",
                    "thumbnail_url": "https://url/test_thumbnail_3.jpg",
                    "price": "300.00",
                    "discount_rate": "15.00",
                    "discounted_price": 255.0,
                    "remain_count": 0,
                    "purchase_count": 15,
                },
                {
                    "product_id": 2,
                    "description_image_url": "https://url/test_image_2.jpg",
                    "categories": [
                        {"category_id": 1, "name": "category_1"},
                        {"category_id": 2, "name": "category_2"},
                    ],
                    "name": "Test Product 2",
                    "company": "ohYes",
                    "thumbnail_url": "https://url/test_thumbnail_2.jpg",
                    "price": "200.00",
                    "discount_rate": "10.00",
                    "discounted_price": 180.0,
                    "remain_count": 0,
                    "purchase_count": 10,
                },
                {
                    "product_id": 1,
                    "description_image_url": "https://url/test_image_1.jpg",
                    "categories": [{"category_id": 1, "name": "category_1"}],
                    "name": "Test Product 1",
                    "company": "ohYes",
                    "thumbnail_url": "https://url/test_thumbnail_1.jpg",
                    "price": "100.00",
                    "discounted_price": 95.0,
                    "discount_rate": "5.00",
                    "remain_count": 0,
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
                    "description_image_url": "https://url/test_image_3.jpg",
                    "categories": [
                        {"category_id": 1, "name": "category_1"},
                        {"category_id": 3, "name": "category_3"},
                    ],
                    "name": "Test Product 3",
                    "company": "ohYes",
                    "thumbnail_url": "https://url/test_thumbnail_3.jpg",
                    "price": "300.00",
                    "discount_rate": "15.00",
                    "discounted_price": 255.0,
                    "remain_count": 0,
                    "purchase_count": 15,
                },
                {
                    "product_id": 2,
                    "description_image_url": "https://url/test_image_2.jpg",
                    "categories": [
                        {"category_id": 1, "name": "category_1"},
                        {"category_id": 2, "name": "category_2"},
                    ],
                    "name": "Test Product 2",
                    "company": "ohYes",
                    "thumbnail_url": "https://url/test_thumbnail_2.jpg",
                    "price": "200.00",
                    "discount_rate": "10.00",
                    "discounted_price": 180.0,
                    "remain_count": 0,
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
                    "description_image_url": "https://url/test_image_3.jpg",
                    "categories": [
                        {"category_id": 1, "name": "category_1"},
                        {"category_id": 3, "name": "category_3"},
                    ],
                    "name": "Test Product 3",
                    "company": "ohYes",
                    "thumbnail_url": "https://url/test_thumbnail_3.jpg",
                    "price": "300.00",
                    "discount_rate": "15.00",
                    "discounted_price": 255.0,
                    "remain_count": 0,
                    "purchase_count": 15,
                }
            ],
        }

    def test_상품_카테고리_조회_테스트(self, api_client, 테스트_여러_상품_생성):
        url = reverse("category-list")

        response = api_client.get(url)

        assert response.json() == [
            {
                "category_id": 1,
                "name": "category_1",
                "subcategories": [{"category_id": 2, "name": "category_2"}],
            },
            {"category_id": 3, "name": "category_3", "subcategories": []},
        ]

    def test_모든_상품_조회_페이징_테스트(self, api_client, 테스트_대량_상품_생성):
        pass
