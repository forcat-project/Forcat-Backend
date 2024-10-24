from decimal import Decimal

import pytest

from django.urls import reverse
from freezegun import freeze_time
from rest_framework.test import APIClient

from account.models import User
from product.models import Product, Category, ProductCategory, Cart, CartItem


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
def 테스트_한글_이름_여러_상품_생성():
    category_1 = Category.objects.create(name="카테고리_1")
    category_2 = Category.objects.create(name="카테고리_2")

    product_1 = Product.objects.create(
        product_id=1,
        name="고양이_사료_맛있다",
        company="삼성",
        thumbnail_url=f"https://url/test_thumbnail.jpg",
        description_image_url=f"https://url/test_image.jpg",
        price=Decimal("1000"),
        discount_rate=Decimal(f"5"),
        purchase_count=300,
    )

    product_2 = Product.objects.create(
        product_id=2,
        name="고양이_사료_맛없다",
        company="삼성",
        thumbnail_url=f"https://url/test_thumbnail.jpg",
        description_image_url=f"https://url/test_image.jpg",
        price=Decimal("1000"),
        discount_rate=Decimal(f"5"),
        purchase_count=300,
    )

    product_3 = Product.objects.create(
        product_id=3,
        name="고양이 맛있다",
        company="삼성",
        thumbnail_url=f"https://url/test_thumbnail.jpg",
        description_image_url=f"https://url/test_image.jpg",
        price=Decimal("1000"),
        discount_rate=Decimal(f"5"),
        purchase_count=300,
    )

    ProductCategory.objects.create(product=product_1, category=category_1)
    ProductCategory.objects.create(product=product_2, category=category_2)
    ProductCategory.objects.create(product=product_3, category=category_2)


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


@pytest.fixture()
def 테스트_67카테고리_생성():
    # 카테고리 생성
    category_67 = Category.objects.create(category_id=67, name="카테고리_67")
    category_68 = Category.objects.create(
        name="카테고리_68", parent_category=category_67
    )

    return category_67, category_68


@pytest.fixture()
def 테스트_장바구니_상품_생성():
    user = User.objects.create(username="테스트_유저", nickname="테스트_닉네임")
    cart = Cart.objects.create(user=user)

    product_1 = Product.objects.create(
        product_id=1,
        name="테스트_상품_1",
        thumbnail_url="http://product_1",
        price=1000,
        remain_count=1,
    )

    product_2 = Product.objects.create(
        product_id=2,
        name="테스트_상품_2",
        thumbnail_url="http://product_2",
        price=2000,
        remain_count=1,
    )

    product_3 = Product.objects.create(
        product_id=3,
        name="테스트_상품_3",
        thumbnail_url="http://product_3",
        price=3000,
        remain_count=2,
    )

    CartItem.objects.create(cart=cart, product=product_1)
    CartItem.objects.create(cart=cart, product=product_2)


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

    def test_모든_상품_조회_이름_필터링_테스트(
        self, api_client, 테스트_한글_이름_여러_상품_생성
    ):
        # with CaptureQueriesContext(connection) as ctx:
        url = reverse("product-list")

        response = api_client.get(url + "?name=맛있다")

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
        url = reverse("category-detail", kwargs={"pk": 67})

        response = api_client.get(url)

        assert response.json() == {"category_id": 67, "name": "카테고리_67"}


@pytest.mark.django_db
class TestProductOrdering:
    def test_상품_할인율_내림차순_정렬_테스트(self, api_client, 테스트_여러_상품_생성):
        # 쿼리 파라미터로 ordering=-discount_rate를 전달
        url = "/api/products?ordering=-discount_rate"

        # GET 요청으로 discount_rate 기준 내림차순 정렬된 상품 조회
        response = api_client.get(url)

        # 응답이 200 OK인지 확인
        assert response.status_code == 200

        # 페이지네이션 구조에서 results 항목만 확인
        results = response.json().get("results", [])

        # 응답 데이터가 discount_rate 기준으로 내림차순 정렬되었는지 확인
        assert results[0]["discount_rate"] == "15.00"  # 첫 번째 상품의 할인율
        assert results[1]["discount_rate"] == "10.00"  # 두 번째 상품의 할인율
        assert results[2]["discount_rate"] == "5.00"  # 세 번째 상품의 할인율

    def test_상품_구매횟수_내림차순_정렬_테스트(
        self, api_client, 테스트_여러_상품_생성
    ):
        # 쿼리 파라미터로 ordering=-purchase_count를 전달
        url = "/api/products?ordering=-purchase_count"

        # GET 요청으로 purchase_count 기준 내림차순 정렬된 상품 조회
        response = api_client.get(url)

        # 응답이 200 OK인지 확인
        assert response.status_code == 200

        # 페이지네이션 구조에서 results 항목만 확인
        results = response.json().get("results", [])

        # 응답 데이터가 purchase_count 기준으로 내림차순 정렬되었는지 확인
        assert results[0]["purchase_count"] == 15  # 첫 번째 상품의 구매 횟수
        assert results[1]["purchase_count"] == 10  # 두 번째 상품의 구매 횟수
        assert results[2]["purchase_count"] == 5  # 세 번째 상품의 구매 횟수


@pytest.mark.django_db
class TestCartItem:
    def test_장바구니_상품_조회_테스트(self, api_client, 테스트_장바구니_상품_생성):
        url = reverse("user-cart-items", kwargs={"user_id": 1})

        res = api_client.get(url)

        assert res.json() == [
            {
                "product": {
                    "product_id": 1,
                    "discounted_price": 1000.0,
                    "name": "테스트_상품_1",
                    "thumbnail_url": "http://product_1",
                    "company": None,
                    "price": "1000.00",
                    "discount_rate": "0.00",
                },
                "quantity": 1,
            },
            {
                "product": {
                    "product_id": 2,
                    "discounted_price": 2000.0,
                    "name": "테스트_상품_2",
                    "thumbnail_url": "http://product_2",
                    "company": None,
                    "price": "2000.00",
                    "discount_rate": "0.00",
                },
                "quantity": 1,
            },
        ]

    def test_장바구니_상품_추가_테스트(self, api_client, 테스트_장바구니_상품_생성):
        url = reverse("user-cart-items", kwargs={"user_id": 1})

        api_client.post(url, data={"product_id": 3, "quantity": 2}, format="json")

        res = api_client.get(url)
        assert res.json() == [
            {
                "product": {
                    "product_id": 1,
                    "discounted_price": 1000.0,
                    "name": "테스트_상품_1",
                    "thumbnail_url": "http://product_1",
                    "company": None,
                    "price": "1000.00",
                    "discount_rate": "0.00",
                },
                "quantity": 1,
            },
            {
                "product": {
                    "product_id": 2,
                    "discounted_price": 2000.0,
                    "name": "테스트_상품_2",
                    "thumbnail_url": "http://product_2",
                    "company": None,
                    "price": "2000.00",
                    "discount_rate": "0.00",
                },
                "quantity": 1,
            },
            # 추가된 3번 제품
            {
                "product": {
                    "product_id": 3,
                    "discounted_price": 3000.0,
                    "name": "테스트_상품_3",
                    "thumbnail_url": "http://product_3",
                    "company": None,
                    "price": "3000.00",
                    "discount_rate": "0.00",
                },
                "quantity": 2,
            },
        ]

    def test_장바구니_상품_업데이트_테스트(self, api_client, 테스트_장바구니_상품_생성):
        url = reverse("user-cart-item", kwargs={"user_id": 1, "products_id": 1})

        res = api_client.patch(url, data={"quantity": 3}, format="json")

        assert res.json() == {"quantity": 3}

    def test_장바구니_상품_삭제_테스트(self, api_client, 테스트_장바구니_상품_생성):
        url = reverse("user-cart-item", kwargs={"user_id": 1, "products_id": 1})

        api_client.delete(url)

        get_url = reverse("user-cart-items", kwargs={"user_id": 1})

        res = api_client.get(get_url)

        assert res.json() == [
            {
                "product": {
                    "product_id": 2,
                    "discounted_price": 2000.0,
                    "name": "테스트_상품_2",
                    "thumbnail_url": "http://product_2",
                    "company": None,
                    "price": "2000.00",
                    "discount_rate": "0.00",
                },
                "quantity": 1,
            }
        ]


@pytest.mark.django_db
def test_67카테고리_조회_테스트(api_client, 테스트_67카테고리_생성):
    # 카테고리 목록을 조회하는 API 경로
    url = reverse("category-list")

    # GET 요청으로 카테고리 목록 조회
    response = api_client.get(url)

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["category_id"] == 67
    assert data[0]["name"] == "카테고리_67"
