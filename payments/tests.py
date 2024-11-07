from datetime import datetime
from decimal import Decimal

import pytest
import json
from django.urls import reverse
from django.test import Client
from freezegun import freeze_time

from payments.models import Order, ProductOrder, Transaction
from payments.service import confirm_payment_success, confirm_payment_failure
from account.models import User
from product.models import Product
from unittest.mock import patch


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def test_유저():
    # 테스트용 유저 생성
    return User.objects.create(
        username="테스트유저",
        nickname="testnickname",
        password="password",
    )


@pytest.fixture()
@freeze_time("2024-10-24 10:10:10")
def test_주문서_생성(test_유저):
    # 거래 정보 더미 데이터 생성 (Transaction은 이미 정의된 모델이라 가정)
    transaction = Transaction.objects.create(
        user=test_유저,
        amount=Decimal("500.00"),
        status="completed",
    )

    transaction_2 = Transaction.objects.create(
        user=test_유저,
        amount=Decimal("500.00"),
        status="completed",
    )

    order = Order.objects.create(
        id="order_12345",
        user=test_유저,
        payment=transaction,
        order_date=datetime.now(),
        original_amount=Decimal("1000.00"),
        points_used=Decimal("100.00"),
        total_amount=Decimal("900.00"),
        user_name="테스트 유저",
        phone_number="010-1234-5678",
        shipping_address="서울특별시 강남구",
        shipping_address_detail="테스트 상세 주소",
        status="completed",
        payment_method="card",
        shipping_status="preparing",
        shipping_memo="부재 시 경비실에 맡겨주세요.",
    )

    order_2 = Order.objects.create(
        id="gpgpgpgp",
        user=test_유저,
        payment=transaction_2,
        order_date=datetime.now(),
        original_amount=Decimal("1000.00"),
        points_used=Decimal("100.00"),
        total_amount=Decimal("900.00"),
        user_name="테스트 유저",
        phone_number="010-1234-5678",
        shipping_address="서울특별시 강남구",
        shipping_address_detail="테스트 상세 주소",
        status="completed",
        payment_method="card",
        shipping_status="preparing",
        shipping_memo="부재 시 경비실에 맡겨주세요.",
    )

    # 상품 주문 정보 더미 데이터 생성
    ProductOrder.objects.create(
        product_name="야옹야옹 고양이 간식",
        price=Decimal("100.00"),
        quantity=2,
        order=order,
        discount_rate=Decimal("5.00"),
        product_id=123,
        product_company="야옹야옹 컴퍼니",
        product_image="https://example.com/product_image.jpg",
    )

    ProductOrder.objects.create(
        product_name="야옹이 놀잇감",
        price=Decimal("100.00"),
        quantity=2,
        order=order,
        discount_rate=Decimal("5.00"),
        product_id=123,
        product_company="야옹야옹 컴퍼니 오야붕",
        product_image="https://example.com/product_image.jpg",
    )

    ProductOrder.objects.create(
        product_name="야옹이 놀잇감",
        price=Decimal("100.00"),
        quantity=2,
        order=order_2,
        discount_rate=Decimal("5.00"),
        product_id=123,
        product_company="야옹야옹 컴퍼니 오야붕",
        product_image="https://example.com/product_image.jpg",
    )


@pytest.mark.django_db
def test_주문_생성_성공(client, test_유저):
    # 필요한 Product 데이터 생성
    Product.objects.create(
        product_id=1,
        name="상품1",
        thumbnail_url="http://example.com/image1.jpg",
        company="회사1",
        price=3000,
        remain_count=10,
    )
    Product.objects.create(
        product_id=2,
        name="상품2",
        thumbnail_url="http://example.com/image2.jpg",
        company="회사2",
        price=2000,
        remain_count=10,
    )

    url = reverse("order", kwargs={"user_id": 1})

    주문_데이터 = {
        "orderId": "test_order_123",
        "originalAmount": 5000,
        "amount": 4000,
        "pointsUsed": 1000,
        "userId": test_유저.id,
        "userName": "테스트유저",
        "phoneNumber": "010-1234-5678",
        "shippingAddress": "서울시 강남구...",
        "shippingAddressDetail": "101호",
        "shippingMemo": "부재시 문 앞에 놔둬주세요!",
        "paymentMethod": "card",
        "products": [
            {
                "product_id": 1,
                "product_name": "상품1",
                "price": 3000,
                "quantity": 1,
                "product_image": "http://example.com/image1.jpg",
            },
            {
                "product_id": 2,
                "product_name": "상품2",
                "price": 2000,
                "quantity": 2,
                "product_image": "http://example.com/image2.jpg",
            },
        ],
    }

    response = client.post(
        url, data=json.dumps(주문_데이터), content_type="application/json"
    )

    # 상태 코드가 200인지 확인
    assert response.status_code == 200
    assert response.json() == {
        "status": "주문이 생성되었습니다",
        "orderId": "test_order_123",
    }


@pytest.mark.django_db
def test_주문_생성_성공(client, test_유저):
    # 필요한 Product 데이터 생성
    Product.objects.create(
        product_id=1,
        name="상품1",
        thumbnail_url="http://example.com/image1.jpg",
        company="회사1",
        price=3000,
        remain_count=10,
    )
    Product.objects.create(
        product_id=2,
        name="상품2",
        thumbnail_url="http://example.com/image2.jpg",
        company="회사2",
        price=2000,
        remain_count=10,
    )

    # order-list URL 생성
    url = reverse("order-list")

    주문_데이터 = {
        "orderId": "test_order_123",
        "originalAmount": 5000,
        "amount": 4000,
        "pointsUsed": 1000,
        "userId": test_유저.id,
        "userName": "테스트유저",
        "phoneNumber": "010-1234-5678",
        "shippingAddress": "서울시 강남구...",
        "shippingAddressDetail": "101호",
        "shippingMemo": "부재시 문 앞에 놔둬주세요!",
        "paymentMethod": "card",
        "products": [
            {
                "product_id": 1,
                "product_name": "상품1",
                "price": 3000,
                "quantity": 1,
                "product_image": "http://example.com/image1.jpg",
            },
            {
                "product_id": 2,
                "product_name": "상품2",
                "price": 2000,
                "quantity": 2,
                "product_image": "http://example.com/image2.jpg",
            },
        ],
    }

    response = client.post(
        url, data=json.dumps(주문_데이터), content_type="application/json"
    )

    # 상태 코드가 200인지 확인
    assert response.status_code == 200
    assert response.json() == {
        "status": "주문이 생성되었습니다",
        "orderId": "test_order_123",
    }


@pytest.mark.django_db
def test_주문_생성_매개변수_누락(client):
    # 필수 매개변수 누락 시도
    url = reverse("order-list", kwargs={"user_id": 1})
    불완전한_데이터 = {
        "orderId": "test_order_123",
        # "amount"와 "userId"가 누락됨
        "shippingAddress": "서울시 강남구...",
    }
    response = client.post(
        url, data=json.dumps(불완전한_데이터), content_type="application/json"
    )

    # 상태 코드가 400인지 확인
    assert response.status_code == 400
    assert response.json() == {"error": "필요한 매개변수가 누락되었습니다."}


@pytest.mark.django_db
def test_결제_성공_서비스_확인(test_유저):
    # 주문 생성
    order = Order.objects.create(
        id="test_order_123",
        user=test_유저,
        total_amount=4000,
        original_amount=5000,
        shipping_address="서울시 강남구...",
        payment_method="card",
        shipping_status="결제 대기중",
        shipping_memo="부재시 문 앞에 놔둬주세요!",
        points_used=1000,
    )

    # ProductOrder 데이터 생성
    ProductOrder.objects.create(
        product_id=1,
        product_name="상품1",
        price=3000,
        quantity=1,
        order=order,
    )
    ProductOrder.objects.create(
        product_id=2,
        product_name="상품2",
        price=2000,
        quantity=2,
        order=order,
    )

    # 결제 성공 데이터 설정
    response_data = {
        "totalAmount": 4000,
        "lastTransactionKey": "mock_transaction_key",
        "receipt": {"url": "https://mock.receipt.url"},
        "method": "card",
    }

    # 결제 성공 함수 호출
    result = confirm_payment_success(order, response_data)

    # 결과 검증
    assert result["status"] == "결제 완료"
    assert result["data"] == response_data
    assert result["user_id"] == test_유저.id
    assert result["order_id"] == order.id

    # Order 및 Transaction 객체가 올바르게 업데이트되었는지 확인
    order.refresh_from_db()
    assert order.shipping_status == "배송 준비중"
    assert order.status == "결제 완료"
    assert order.payment_method == "card"

    # Transaction 객체가 생성되었는지 확인
    payment = Transaction.objects.get(order=order)
    assert payment.amount == order.total_amount
    assert payment.pg_tx_id == "mock_transaction_key"
    assert payment.receipt_url == "https://mock.receipt.url"

    # ProductOrder 정보 확인
    product_orders = ProductOrder.objects.filter(order=order)
    products = [
        {
            "product_name": product.product_name,
            "price": product.price,
            "quantity": product.quantity,
        }
        for product in product_orders
    ]

    assert products == [
        {"product_name": "상품1", "price": 3000, "quantity": 1},
        {"product_name": "상품2", "price": 2000, "quantity": 2},
    ]


@pytest.mark.django_db
def test_결제_실패_서비스_확인(test_유저):
    # 주문 생성
    order = Order.objects.create(
        id="test_order_123",
        user=test_유저,
        total_amount=4000,
        original_amount=5000,
        shipping_address="서울시 강남구...",
        payment_method="card",
        shipping_status="결제 대기중",
        shipping_memo="부재시 문 앞에 놔둬주세요!",
        points_used=1000,
    )

    # 결제 실패 데이터 설정
    response_data = {
        "code": "PAYMENT_FAILED",
        "message": "결제 승인에 실패하였습니다.",
    }

    # 결제 실패 함수 호출
    result = confirm_payment_failure(order, response_data)

    # 결과 검증
    assert result == {
        "code": "PAYMENT_FAILED",
        "message": "결제 승인에 실패하였습니다.",
    }

    # 주문 상태 검증
    order.refresh_from_db()
    assert order.shipping_status == "결제 실패"


@pytest.mark.django_db
def test_주문_생성_성공(client, test_유저):
    # 필요한 Product 데이터 생성
    Product.objects.create(
        product_id=1,
        name="상품1",
        thumbnail_url="http://example.com/image1.jpg",
        company="회사1",
        price=3000,
        remain_count=10,
    )
    Product.objects.create(
        product_id=2,
        name="상품2",
        thumbnail_url="http://example.com/image2.jpg",
        company="회사2",
        price=2000,
        remain_count=10,
    )

    # user_id 인자를 포함하여 order-list URL 생성
    url = reverse("order-list", kwargs={"user_id": test_유저.id})

    주문_데이터 = {
        "orderId": "test_order_123",
        "originalAmount": 5000,
        "amount": 4000,
        "pointsUsed": 1000,
        "userId": test_유저.id,
        "userName": "테스트유저",
        "phoneNumber": "010-1234-5678",
        "shippingAddress": "서울시 강남구...",
        "shippingAddressDetail": "101호",
        "shippingMemo": "부재시 문 앞에 놔둬주세요!",
        "paymentMethod": "card",
        "products": [
            {
                "product_id": 1,
                "product_name": "상품1",
                "price": 3000,
                "quantity": 1,
                "product_image": "http://example.com/image1.jpg",
            },
            {
                "product_id": 2,
                "product_name": "상품2",
                "price": 2000,
                "quantity": 2,
                "product_image": "http://example.com/image2.jpg",
            },
        ],
    }

    response = client.post(
        url, data=json.dumps(주문_데이터), content_type="application/json"
    )

    # 상태 코드가 200인지 확인
    assert response.status_code == 200
    assert response.json() == {
        "status": "주문이 생성되었습니다",
        "orderId": "test_order_123",
    }


@pytest.mark.django_db
def test_주문_취소(client, test_유저, test_주문서_생성):
    # 주문의 ID를 사용하여 취소 테스트
    order_id = "order_12345"
    url = reverse(
        "order-detail", kwargs={"user_id": test_유저.id, "order_id": order_id}
    )

    # DELETE 요청으로 주문 취소
    response = client.delete(url)

    # 응답이 성공적인지 확인
    assert response.status_code == 200
    assert response.json() == {"message": "Order has been successfully deleted."}

    # 삭제 후 주문 조회하여 cancellation_date 확인
    response_get = client.get(url)
    assert response_get.status_code == 200

    # 조회된 주문 데이터에서 cancellation_date 확인
    cancled_order_data = response_get.json()
    assert cancled_order_data["order_info"]["cancellation_date"] is not None


@pytest.mark.django_db
def test_주문_업데이트(client, test_유저, test_주문서_생성):
    # 주문의 ID를 사용하여 취소 테스트
    order_id = "order_12345"
    url = reverse(
        "order-cancel", kwargs={"user_id": test_유저.id, "order_id": order_id}
    )
    response = client.patch(url)

    # 주문이 취소 처리가 되었는지 확인
    updated_order = Order.objects.get(id=order_id)
    assert updated_order.status == "canceled"
    assert updated_order.shipping_status == "canceled"
    assert updated_order.payment.status == "canceled"

    # 응답이 성공적인지 확인
    assert response.status_code == 200
    print(response.json())
    assert response.json() == {
        "message": "Order payment has been successfully updated."
    }
