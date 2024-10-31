import requests
import base64
import json
from django.conf import settings
from django.http import JsonResponse
from payments.models import Order, ProductOrder
from django.views.decorators.csrf import csrf_exempt
from payments.service import confirm_payment_success, confirm_payment_failure
from account.models import User
from payments.constants import ERROR_MESSAGES
import logging

logger = logging.getLogger(__name__)


@csrf_exempt
def create_order(request):
    if request.method != "POST":
        return JsonResponse(
            {"error": ERROR_MESSAGES["invalid_request_method"]}, status=405
        )

    try:
        data = json.loads(request.body)
        logger.info(f"요청 데이터: {data}")

        order_id = data.get("orderId")
        original_amount = data.get("originalAmount")
        points_used = data.get("pointsUsed")
        amount = data.get("amount")
        user_id = data.get("userId")
        shipping_address = data.get("shippingAddress")
        shipping_memo = data.get("shippingMemo")
        payment_method = data.get("paymentMethod")
        user_name = data.get("userName")
        phone_number = data.get("phoneNumber")
        products = data.get("products", [])
        # 입력 데이터 유효성 검사
        if not all([order_id, amount, user_id, user_name, phone_number]):
            return JsonResponse(
                {"error": ERROR_MESSAGES["missing_parameters"]}, status=400
            )

        # 사용자 정보를 가져옵니다.
        user = User.objects.filter(id=user_id).first()
        if not user:
            return JsonResponse({"error": ERROR_MESSAGES["user_not_found"]}, status=404)

        # 주문을 생성합니다.
        order = Order.objects.create(
            id=order_id,
            user=user,
            user_name=user_name,
            phone_number=phone_number,
            total_amount=amount,
            original_amount=original_amount,
            shipping_address=shipping_address,
            payment_method=payment_method,
            shipping_status="결제 대기중",
            shipping_memo=shipping_memo,
            points_used=points_used,
        )
        for product in products:
            ProductOrder.objects.create(
                product_name=product["product_name"],
                price=product["price"],
                quantity=product["quantity"],
                order=order,
                product_id=product["product_id"],
                discount_rate=product.get("discount_rate", 0),
                product_company=product.get("product_company", "포캣"),
            )
        logger.info("모든 제품이 성공적으로 저장되었습니다.")
        return JsonResponse({"status": "주문이 생성되었습니다", "orderId": order.id})

    except json.JSONDecodeError:
        return JsonResponse({"error": ERROR_MESSAGES["invalid_json"]}, status=400)
    except Exception as e:
        logger.error(f"주문 생성 중 오류 발생: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def confirm_payment(request):
    logger.info("confirm_payment 함수가 호출되었습니다.")
    if request.method != "POST":
        return JsonResponse(
            {"error": ERROR_MESSAGES["invalid_request_method"]}, status=405
        )

    try:
        data = json.loads(request.body)
        payment_key = data.get("paymentKey")
        order_id = data.get("orderId")
        amount = float(data.get("amount"))
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": ERROR_MESSAGES["invalid_json"]}, status=400)

    # 요청 값 검증
    if not all([payment_key, order_id, amount]):
        return JsonResponse({"error": ERROR_MESSAGES["missing_parameters"]}, status=400)

    # Order 조회 및 금액 검증
    order = Order.objects.filter(id=order_id).first()
    if not order:
        logger.error(f"{ERROR_MESSAGES['order_not_found']}: {order_id}")
        return JsonResponse({"error": ERROR_MESSAGES["order_not_found"]}, status=404)

    # 결제 금액 검증
    expected_total_amount = order.original_amount - order.points_used
    if expected_total_amount != order.total_amount:
        logger.error(
            f"{ERROR_MESSAGES['amount_mismatch']}: 예상 금액 {expected_total_amount}, 실제 결제 금액 {order.total_amount}"
        )
        return JsonResponse(
            {
                "error_code": "amount_mismatch",
                "error_message": ERROR_MESSAGES["amount_mismatch"],
            },
            status=400,
        )

    # Toss Payments 인증 헤더 생성
    secret_key = settings.TOSS_SECRET_KEY
    encoded_secret_key = (
        "Basic " + base64.b64encode((secret_key + ":").encode()).decode()
    )
    headers = {"Authorization": encoded_secret_key, "Content-Type": "application/json"}

    # Toss Payments 결제 승인 요청
    try:
        response = requests.post(
            settings.TOSS_CONFIRM_API_URL,
            json={"orderId": order_id, "amount": amount, "paymentKey": payment_key},
            headers=headers,
        )
        response_data = response.json()

        if response.status_code == 200:
            # 결제 성공 처리
            result = confirm_payment_success(order, response_data)
            print(result)
            return JsonResponse(result)
        else:
            # 결제 실패 시 처리
            result = confirm_payment_failure(order, response_data)
            return JsonResponse(result, status=response.status_code)

    except requests.exceptions.RequestException as e:
        logger.error(f"{ERROR_MESSAGES['payment_failed']}: {str(e)}")
        return JsonResponse(
            {"error": ERROR_MESSAGES["payment_failed"], "details": str(e)}, status=400
        )
