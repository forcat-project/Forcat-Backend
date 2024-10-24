from decimal import Decimal
import pytest
from django.urls import reverse
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
    category_1 = Category.objects.create(name="category_1")
    category_2 = Category.objects.create(name="category_2", parent_category=category_1)
    category_3 = Category.objects.create(name="category_3")

    for i in range(1, 4):
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

        ProductCategory.objects.create(product=product, category=category_1)
        if i % 2 == 0:
            ProductCategory.objects.create(product=product, category=category_2)
        elif i % 3 == 0:
            ProductCategory.objects.create(product=product, category=category_3)

@pytest.fixture()
def 테스트_한글_이름_여러_상품_생성():
    category_1 = Category.objects.create(name="카테고리_1")
    category_2 = Category.objects.create(name="카테고리_2")

    products = [
        {"id": 1, "name": "고양이_사료_맛있다"},
        {"id": 2, "name": "고양이_사료_맛없다"},
        {"id": 3, "name": "고양이 맛있다"},
    ]

    for product_data in products:
        product = Product.objects.create(
            product_id=product_data["id"],
            name=product_data["name"],
            company="삼성",
            thumbnail_url="https://url/test_thumbnail.jpg",
            description_image_url="https://url/test_image.jpg",
            price=Decimal("1000"),
            discount_rate=Decimal("5"),
            purchase_count=300,
        )
        if product_data["id"] == 1:
            ProductCategory.objects.create(product=product, category=category_1)
        else:
            ProductCategory.objects.create(product=product, category=category_2)

@pytest.fixture()
def 테스트_대량_상품_생성():
    category_1 = Category.objects.create(name="category_1")
    category_2 = Category.objects.create(name="category_2", parent_category=category_1)
    category_3 = Category.objects.create(name="category_3")

    for i in range(1, 20):
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

        ProductCategory.objects.create(product=product, category=category_1)
        if i % 2 == 0:
            ProductCategory.objects.create(product=product, category=category_2)
        elif i % 3 == 0:
            ProductCategory.objects.create(product=product, category=category_3)

@pytest.fixture()
def 테스트_67카테고리_생성():
    category_67 = Category.objects.create(category_id=67, name="카테고리_67")
    category_68 = Category.objects.create(name="카테고리_68", parent_category=category_67)
    return category_67, category_68


@pytest.mark.django_db
class TestProductCRUD:
    def test_특정_상품_조회_테스트(self, api_client, 테스트_상품_생성):
        url = reverse("product-detail", kwargs={"pk": 1})
        response = api_client.get(url)
        assert response.status_code == 200
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
        assert response.status_code == 200
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
                    "discount_rate": "5.00",
                    "discounted_price": 95.0,
                    "remain_count": 0,
                    "purchase_count": 5,
                },
            ],
        }

    def test_모든_상품_조회_카테고리_필터링_테스트(self, api_client, 테스트_여러_상품_생성):
        url = reverse("product-list")
        response = api_client.get(url + "?categories=2&categories=3")
        assert response.status_code == 200
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

    def test_모든_상품_조회_이름_필터링_테스트(self, api_client, 테스트_한글_이름_여러_상품_생성):
        url = reverse("product-list")
        response = api_client.get(url + "?name=맛있다")
        assert response.status_code == 200
        assert response.json() == {
            "next": None,
            "previous": None,
            "results": [
                {
                    "product_id": 3,
                    "categories": [{"category_id": 2, "name": "카테고리_2"}],
                    "discounted_price": 950.0,
                    "name": "고양이 맛있다",
                    "thumbnail_url": "https://url/test_thumbnail.jpg",
                    "company": "삼성",
                    "description_image_url": "https://url/test_image.jpg",
                    "price": "1000.00",
                    "discount_rate": "5.00",
                    "remain_count": 0,
                    "purchase_count": 300,
                },
                {
                    "product_id": 1,
                    "categories": [{"category_id": 1, "name": "카테고리_1"}],
                    "discounted_price": 950.0,
                    "name": "고양이_사료_맛있다",
                    "thumbnail_url": "https://url/test_thumbnail.jpg",
                    "company": "삼성",
                    "description_image_url": "https://url/test_image.jpg",
                    "price": "1000.00",
                    "discount_rate": "5.00",
                    "remain_count": 0,
                    "purchase_count": 300,
                },
            ],
        }

    def test_상품_카테고리_조회_테스트(self, api_client, 테스트_여러_상품_생성):
        url = reverse("category-list")
        response = api_client.get(url)
        assert response.status_code == 200
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

    def test_특정_카테고리_조회_테스트(self, api_client, 테스트_67카테고리_생성):
        url = reverse("category-list")
        response = api_client.get(url)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["category_id"] == 67
        assert data[0]["name"] == "카테고리_67"
        assert len(data[0]["subcategories"]) == 1
        assert data[0]["subcategories"][0]["category_id"] == 68
        assert data[0]["subcategories"][0]["name"] == "카테고리_68"


@pytest.mark.django_db
class TestProductOrdering:
    def test_상품_할인율_내림차순_정렬_테스트(self, api_client, 테스트_여러_상품_생성):
        url = "/api/products?ordering=-discount_rate"
        response = api_client.get(url)
        assert response.status_code == 200
        results = response.json().get("results", [])
        assert results[0]["discount_rate"] == "15.00"
        assert results[1]["discount_rate"] == "10.00"
        assert results[2]["discount_rate"] == "5.00"

    def test_상품_구매횟수_내림차순_정렬_테스트(self, api_client, 테스트_여러_상품_생성):
        url = "/api/products?ordering=-purchase_count"
        response = api_client.get(url)
        assert response.status_code == 200
        results = response.json().get("results", [])
        assert results[0]["purchase_count"] == 15
        assert results[1]["purchase_count"] == 10
        assert results[2]["purchase_count"] == 5


@pytest.mark.django_db
class TestDiscountRateFiltering:
    def test_할인율_내림차순_정렬_테스트(self, api_client):
        # Product 생성
        product_1 = Product.objects.create(
            product_id=1,
            name="Product 1",
            company="Company A",
            thumbnail_url="https://url/product1.jpg",
            description_image_url="https://url/product1_desc.jpg",
            price=Decimal("100.00"),
            discount_rate=Decimal("0.00"),
            purchase_count=10,
        )
        product_2 = Product.objects.create(
            product_id=2,
            name="Product 2",
            company="Company B",
            thumbnail_url="https://url/product2.jpg",
            description_image_url="https://url/product2_desc.jpg",
            price=Decimal("200.00"),
            discount_rate=Decimal("15.00"),
            purchase_count=5,
        )
        product_3 = Product.objects.create(
            product_id=3,
            name="Product 3",
            company="Company C",
            thumbnail_url="https://url/product3.jpg",
            description_image_url="https://url/product3_desc.jpg",
            price=Decimal("150.00"),
            discount_rate=Decimal("10.00"),
            purchase_count=8,
        )

        url = "/api/products?ordering=-discount_rate"
        response = api_client.get(url)

        assert response.status_code == 200

        print(response.json())

        results = response.json().get('results', [])

        assert results[0] == {
            'product_id': product_2.product_id,
            'name': product_2.name,
            'company': product_2.company,
            'thumbnail_url': product_2.thumbnail_url,
            'description_image_url': product_2.description_image_url,
            'price': "200.00",
            'discount_rate': "15.00",
            'purchase_count': product_2.purchase_count,
            'categories': [],
            'discounted_price': 170.0,
            'remain_count': 0,
        }
        assert results[1] == {
            'product_id': product_3.product_id,
            'name': product_3.name,
            'company': product_3.company,
            'thumbnail_url': product_3.thumbnail_url,
            'description_image_url': product_3.description_image_url,
            'price': "150.00",
            'discount_rate': "10.00",
            'purchase_count': product_3.purchase_count,
            'categories': [],
            'discounted_price': 135.0,
            'remain_count': 0,
        }



