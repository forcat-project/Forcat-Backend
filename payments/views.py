# views.py
from tosspayments import Tosspayments
from django.conf import settings
from django.http import JsonResponse
from .models import Order, Payment, ProductOrder

# Toss Payments 클라이언트 초기화
toss_client = Tosspayments(settings.TOSS_SECRET_KEY)


def confirm_payment(request):
    payment_key = request.GET.get("paymentKey")
    order_id = request.GET.get("orderId")
    amount = request.GET.get("amount")
    Tosspayments.confirm_payment(payment_key, order_id, amount)

    try:
        # Toss로 결제 승인 요청
        response = toss_client.confirm_payment(
            paymentKey=payment_key, orderId=order_id, amount=amount
        )

        if response["status"] == "DONE":  # 결제 성공 확인
            # 주문 내역 찾기
            order = Order.objects.get(id=order_id)

            # 결제 정보 저장 (새로운 Payment 객체 생성)
            payment = Payment.objects.create(
                amount=amount,
                user=order.user,
                status="completed",  # 결제 완료 상태로 저장
                pg_tx_id=response["transactionKey"],  # Toss에서 받은 거래 ID
                receipt_url=response["receipt"]["url"],  # 영수증 URL
            )

            # 주문에 결제 정보 연결
            order.payment = payment
            order.shipping_status = "배송 준비"  # 배송 준비 상태로 업데이트
            order.save()

            return JsonResponse({"status": "Payment confirmed", "data": response})
        else:
            return JsonResponse({"error": "Payment not completed"}, status=400)

    except Order.DoesNotExist:
        return JsonResponse({"error": "Order not found"}, status=404)
    except Exception as e:
        # Toss 결제 승인 처리 실패 시
        return JsonResponse({"error": str(e)}, status=400)
