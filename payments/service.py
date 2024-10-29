# payments/service.py

from payments.models import Transaction, ProductOrder
import logging

logger = logging.getLogger(__name__)


def confirm_payment_success(order, response_data):
    try:
        # 결제 성공 처리
        payment = Transaction.objects.create(
            amount=order.total_amount,
            user=order.user,
            status="결제 완료",
            pg_tx_id=response_data.get("lastTransactionKey"),
            receipt_url=response_data.get("receipt", {}).get("url"),
        )
        order.payment = payment
        order.shipping_status = "배송 준비중"
        order.payment_method = response_data.get("method")
        order.save()

        # 사용자가 구매한 상품들 다 닮기
        product_orders = ProductOrder.objects.filter(order=order)
        products = [
            {
                "product_name": product.product_name,
                "price": product.price,
                "quantity": product.quantity,
            }
            for product in product_orders
        ]

        logger.info(f"주문 {order.id}에 대한 결제가 확인되었습니다.")
        return {
            "status": "결제 완료",
            "data": response_data,
            "order_info": {
                "order_id": order.id,
                "shipping_memo": order.shipping_memo,
                "points_used": order.points_used,
                "shipping_status": order.shipping_status,
                "payment_method": order.payment_method,
                "original_amount": order.original_amount,
                "products": products,
            },
        }
    except Exception as e:
        logger.error(f"결제 성공 처리 중 오류 발생: {str(e)}")
        raise


def confirm_payment_failure(order, response_data):
    try:
        # 결제 실패 처리
        order.shipping_status = "결제 실패"
        order.save()
        logger.error(f"결제 확인 실패: {response_data}")
        return response_data
    except Exception as e:
        logger.error(f"결제 실패 처리 중 오류 발생: {str(e)}")
        raise
