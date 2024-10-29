import requests
import base64
import json
from django.conf import settings
from django.http import JsonResponse
from payments.models import Order
from django.views.decorators.csrf import csrf_exempt
from payments.service import confirm_payment_success, confirm_payment_failure
from account.models import User
import logging

logger = logging.getLogger(__name__)

# 응답 메시지 상수화
ERROR_MESSAGES = {
    "missing_parameters": "필요한 매개변수가 누락되었습니다.",
    "user_not_found": "유저를 찾을 수 없습니다.",
    "invalid_json": "잘못된 JSON 형식입니다.",
    "order_not_found": "주문을 찾을 수 없습니다.",
    "amount_mismatch": "금액 불일치",
    "payment_failed": "결제 확인에 실패했습니다.",
    "invalid_request_method": "잘못된 요청 방식입니다.",
}


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
        # total_amount = data.get("totalAmount")
        points_used = data.get("pointsUsed")
        amount = data.get("amount")
        user_id = data.get("userId")
        shipping_address = data.get("shippingAddress")
        shipping_memo = data.get("shippingMemo")
        payment_method = data.get("paymentMethod")

        # 입력 데이터 유효성 검사
        if not all([order_id, amount, user_id]):
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
            total_amount=amount,
            original_amount=original_amount,
            shipping_address=shipping_address,
            payment_method=payment_method,
            shipping_status="결제 대기중",
            shipping_memo=shipping_memo,
            points_used=points_used,
        )

        logger.info(f"주문이 성공적으로 생성되었습니다: {order.id}")
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

    if float(order.total_amount) != amount:
        logger.error(
            f"{ERROR_MESSAGES['amount_mismatch']}: 예상 금액 {order.total_amount}, 실제 금액 {amount}"
        )
        return JsonResponse({"error": ERROR_MESSAGES["amount_mismatch"]}, status=400)

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
