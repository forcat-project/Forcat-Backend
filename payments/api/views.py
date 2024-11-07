import requests
import logging
import base64
import json

from drf_yasg import openapi
from account.models import User
from django.conf import settings
from product.models import Product
from django.http import JsonResponse
from .serializers import OrderSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status, mixins
from payments.constants import ERROR_MESSAGES
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from payments.models import Order, ProductOrder
from django.views.decorators.csrf import csrf_exempt
from payments.service import confirm_payment_success, confirm_payment_failure


logger = logging.getLogger(__name__)


class PaymentViewSet(viewsets.ViewSet):

    @swagger_auto_schema(
        method="post",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "paymentKey": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Payment key for the transaction",
                ),
                "orderId": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Unique Order ID"
                ),
                "amount": openapi.Schema(
                    type=openapi.TYPE_NUMBER, description="Amount to be paid"
                ),
            },
            required=["paymentKey", "orderId", "amount"],
        ),
    )
    @action(detail=False, methods=["post"], url_path="confirm")
    @csrf_exempt
    def confirm_payment(self, request):
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
            return JsonResponse(
                {"error": ERROR_MESSAGES["missing_parameters"]}, status=400
            )

        # Order 조회 및 금액 검증
        order = Order.objects.filter(id=order_id).first()
        if not order:
            logger.error(f"{ERROR_MESSAGES['order_not_found']}: {order_id}")
            return JsonResponse(
                {"error": ERROR_MESSAGES["order_not_found"]}, status=404
            )

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
        headers = {
            "Authorization": encoded_secret_key,
            "Content-Type": "application/json",
        }

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
                {"error": ERROR_MESSAGES["payment_failed"], "details": str(e)},
                status=400,
            )


class OrderViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = OrderSerializer

    def get_queryset(self):
        user_id = self.kwargs.get("user_id")
        if user_id is not None:
            return Order.objects.filter(user_id=user_id)
        return Order.objects.none()  # user_id가 없는 경우 빈 쿼리셋 반환

    @swagger_auto_schema(
        method="post",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "orderId": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Unique identifier for the order",
                ),
                "originalAmount": openapi.Schema(
                    type=openapi.TYPE_NUMBER, description="Original amount of the order"
                ),
                "pointsUsed": openapi.Schema(
                    type=openapi.TYPE_NUMBER, description="Points used for this order"
                ),
                "totalAmount": openapi.Schema(
                    type=openapi.TYPE_NUMBER,
                    description="Total amount after points and discounts",
                ),
                "userId": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="ID of the user making the order",
                ),
                "userName": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Name of the user placing the order",
                ),
                "phoneNumber": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Phone number of the user"
                ),
                "shippingAddress": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Primary shipping address"
                ),
                "shippingAddressDetail": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Detailed shipping address"
                ),
                "shippingMemo": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Shipping memo for delivery instructions",
                ),
                "paymentMethod": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Method of payment",
                    enum=[
                        "card",
                        "transfer",
                        "kakaopay",
                        "naverpay",
                        "samsungpay",
                        "virtual_account",
                        "mobile",
                        "point",
                        "other",
                    ],
                ),
                "products": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "product_id": openapi.Schema(
                                type=openapi.TYPE_INTEGER, description="Product ID"
                            ),
                            "product_name": openapi.Schema(
                                type=openapi.TYPE_STRING, description="Product name"
                            ),
                            "price": openapi.Schema(
                                type=openapi.TYPE_NUMBER,
                                description="Price at the time of order",
                            ),
                            "quantity": openapi.Schema(
                                type=openapi.TYPE_INTEGER,
                                description="Quantity ordered",
                            ),
                            "discount_rate": openapi.Schema(
                                type=openapi.TYPE_NUMBER,
                                description="Discount rate applied to the product",
                            ),
                            "product_company": openapi.Schema(
                                type=openapi.TYPE_STRING,
                                description="Company of the product",
                            ),
                            "product_image": openapi.Schema(
                                type=openapi.TYPE_STRING,
                                format="url",
                                description="URL of the product image",
                            ),
                        },
                    ),
                    description="List of products in the order",
                ),
            },
            required=[
                "orderId",
                "totalAmount",
                "userId",
                "userName",
                "phoneNumber",
                "paymentMethod",
                "products",
            ],
        ),
    )
    @action(detail=True, methods=["post"], url_path="create-order")
    @csrf_exempt
    def create_order(self, request, *args, **kwargs):
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
            user_id = kwargs["user_id"]
            shipping_address = data.get("shippingAddress")
            shipping_address_detail = data.get("shippingAddressDetail")
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
                return JsonResponse(
                    {"error": ERROR_MESSAGES["user_not_found"]}, status=404
                )

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
                shipping_address_detail=shipping_address_detail,
                shipping_memo=shipping_memo,
                points_used=points_used,
            )
            # 재고 감소 및 ProductOrder 생성
            for product in products:
                product_id = product["product_id"]
                quantity = product["quantity"]
                product_image = product["product_image"]
                product_obj = Product.objects.get(product_id=product_id)

                # 재고 업데이트
                product_obj.remain_count -= quantity
                product_obj.save()

            for product in products:
                ProductOrder.objects.create(
                    product_name=product["product_name"],
                    price=product["price"],
                    quantity=product["quantity"],
                    order=order,
                    product_id=product["product_id"],
                    discount_rate=product.get("discount_rate", 0),
                    product_company=product.get("product_company", "포캣"),
                    product_image=product.get("product_image"),
                )
            logger.info("모든 제품이 성공적으로 저장되었습니다.")
            return JsonResponse(
                {"status": "주문이 생성되었습니다", "orderId": order.id}
            )

        except json.JSONDecodeError:
            return JsonResponse({"error": ERROR_MESSAGES["invalid_json"]}, status=400)
        except Exception as e:
            logger.error(f"주문 생성 중 오류 발생: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)


@api_view(["GET", "DELETE", "PATCH"])
def order_detail(request, user_id, order_id):
    try:
        logger.info(f"Order 조회 시도 - user_id: {user_id}, order_id: {order_id}")
        order = Order.objects.get(id=order_id, user__id=user_id)

        if request.method == "GET":
            # ProductOrder 정보 조회
            product_orders = ProductOrder.objects.filter(order=order)
            logger.info(
                f"ProductOrder 조회 성공 - order_id: {order_id}, 상품 수: {product_orders.count()}"
            )

            # Order와 ProductOrder 정보 직렬화 및 응답 데이터 생성
            serializer = OrderSerializer(order)
            response_data = {
                "order_info": serializer.data,
                "products": [
                    {
                        "product_name": product.product_name,
                        "price": product.price,
                        "quantity": product.quantity,
                        "product_image": product.product_image,
                        "discount_rate": product.discount_rate,
                    }
                    for product in product_orders
                ],
            }
            logger.info(
                f"응답 데이터 생성 완료 - user_id: {user_id}, order_id: {order_id}"
            )
            return Response(response_data, status=status.HTTP_200_OK)

        elif request.method == "DELETE":
            # 삭제 처리
            order.delete()
            logger.info(f"Order 삭제 성공 - order_id: {order_id}, user_id: {user_id}")
            return Response(
                {"message": "Order has been successfully deleted."},
                status=status.HTTP_200_OK,
            )

        elif request.method == "PATCH":
            # 결제 취소 업데이트 처리
            order.payment.status = "canceled"
            order.shipping_status = "canceled"
            order.status = "canceled"
            order.payment.save()
            order.save()

            logger.info(f"Order 결제 취소 업데이트 성공 - order_id: {order_id}, user_id: {user_id}")
            return Response(
                {"message": "Order payment has been successfully updated."},
                status=status.HTTP_200_OK,
            )

    except Order.DoesNotExist:
        error_message = f"Order with id '{order_id}' for user '{user_id}' not found."
        logger.warning(f"Order 조회 실패: {error_message}")
        return Response({"error": error_message}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.error(f"예상치 못한 오류 발생: {str(e)}")
        return Response(
            {"error": "An unexpected error occurred."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
