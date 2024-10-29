import pytest
import json
from django.urls import reverse
from django.test import Client
from payments.models import Order, ProductOrder, Transaction
from payments.service import confirm_payment_success, confirm_payment_failure
from account.models import User
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
        points=1000,  # 초기 포인트 설정
    )


@pytest.mark.django_db
def test_주문_생성_성공(client, test_유저):
    # create_order 테스트
    url = reverse("create_order")
    주문_데이터 = {
        "orderId": "test_order_123",
        "originalAmount": 5000,
        "amount": 4000,
        "pointsUsed": 1000,
        "userId": test_유저.id,
        "shippingAddress": "서울시 강남구...",
        "shippingMemo": "부재시 문 앞에 놔둬주세요!",
        "paymentMethod": "card",
        "products": [
            {"product_name": "상품1", "price": 3000, "quantity": 1},
            {"product_name": "상품2", "price": 2000, "quantity": 2},
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
@patch("payments.views.requests.post")
def test_결제_확인_성공(mock_post, client, test_유저):
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
        product_name="상품1", price=3000, quantity=1, order=order
    )
    ProductOrder.objects.create(
        product_name="상품2", price=2000, quantity=2, order=order
    )

    # Mocked response 설정
    mock_response = {
        "status": "DONE",
        "lastTransactionKey": "mock_transaction_key",
        "receipt": {"url": "https://mock.receipt.url"},
        "totalAmount": 4000,
        "method": "card",
    }
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = mock_response

    # confirm_payment API 호출
    url = reverse("confirm_payment")
    결제_데이터 = {
        "paymentKey": "test_payment_key_123",
        "orderId": "test_order_123",
        "amount": 4000,
    }
    response = client.post(
        url, data=json.dumps(결제_데이터), content_type="application/json"
    )

    # 상태 코드가 200인지 확인
    assert response.status_code == 200

    # 응답 JSON 확인
    assert response.json() == {
        "status": "결제 완료",
        "data": {
            "status": "DONE",
            "lastTransactionKey": "mock_transaction_key",
            "receipt": {"url": "https://mock.receipt.url"},
            "totalAmount": 4000,
            "method": "card",
        },
        "order_info": {
            "order_id": "test_order_123",
            "shipping_memo": "부재시 문 앞에 놔둬주세요!",
            "points_used": "1000.00",
            "shipping_status": "배송 준비중",
            "payment_method": "card",
            "original_amount": "5000.00",
            "products": [
                {"product_name": "상품1", "price": "3000.00", "quantity": 1},
                {"product_name": "상품2", "price": "2000.00", "quantity": 2},
            ],
        },
    }


@pytest.mark.django_db
def test_주문_생성_매개변수_누락(client):
    # 필수 매개변수 누락 시도
    url = reverse("create_order")
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
def test_결제_성공_확인(test_유저):
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
        product_name="상품1", price=3000, quantity=1, order=order
    )
    ProductOrder.objects.create(
        product_name="상품2", price=2000, quantity=2, order=order
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
    assert result["order_info"]["products"] == [
        {"product_name": "상품1", "price": 3000, "quantity": 1},
        {"product_name": "상품2", "price": 2000, "quantity": 2},
    ]


@pytest.mark.django_db
def test_결제_실패_확인(test_유저):
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
