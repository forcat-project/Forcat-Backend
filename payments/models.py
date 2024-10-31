from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


# 결제 모델
class Transaction(models.Model):
    id = models.AutoField(primary_key=True)  # 결제 TX ID
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # 결제 금액
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )  # 결제 유저 ID (참조)
    payment_date = models.DateTimeField(auto_now_add=True)  # 결제 시간
    status = models.CharField(
        max_length=20,
        choices=[
            ("completed", "결제 완료"),
            ("refunded", "환불 완료"),
            ("failed", "결제 실패"),
        ],
    )  # 결제 상태
    pg_tx_id = models.CharField(max_length=100)  # PG TX ID (외부 결제 서비스 ID)
    receipt_url = models.URLField()  # 결제 영수증 URL

    def __str__(self):
        return f"Transaction {self.id} for {self.user.username}"


# 환불 모델
class Refund(models.Model):
    payment = models.ForeignKey(
        Transaction, on_delete=models.CASCADE, related_name="refunds"
    )  # 환불 대상 결제와의 관계 (1:N)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2)  # 환불 금액
    refund_requested_date = models.DateTimeField(auto_now_add=True)  # 환불 요청 일자
    refund_completed_date = models.DateTimeField(
        null=True, blank=True
    )  # 환불 완료 일자
    status = models.CharField(
        max_length=20,
        choices=[
            ("requested", "환불 요청됨"),
            ("processing", "환불 처리 중"),
            ("completed", "환불 완료"),
            ("rejected", "환불 거절"),
        ],
        default="requested",
    )  # 환불 상태
    reason = models.TextField(null=True, blank=True)  # 환불 사유

    def __str__(self):
        return f"Refund for Payment {self.payment.id} - Amount: {self.refund_amount} - Status: {self.status}"


# 주문 모델
class Order(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    payment = models.OneToOneField(
        Transaction, on_delete=models.SET_NULL, null=True, blank=True
    )
    order_date = models.DateTimeField(auto_now_add=True)
    original_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    points_used = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    user_name = models.CharField(max_length=255, blank=False, null=False, default="Anonymous")  # 사용자 이름
    phone_number = models.CharField(max_length=15, blank=False, null=False, default="000-0000-0000") # 전화번호
    shipping_address_detail = models.CharField(max_length=255, blank=True, null=True)  # 상세 배송지
    payment_method = models.CharField(
        max_length=20,
        choices=[
            ("card", "신용/체크 카드"),
            ("transfer", "계좌 이체"),
            ("kakaopay", "카카오페이"),
            ("naverpay", "네이버페이"),
            ("samsungpay", "삼성페이"),
            ("virtual_account", "가상계좌"),
            ("mobile", "휴대폰 결제"),
            ("point", "포인트"),
            ("other", "기타"),
        ],
    )
    shipping_address = models.CharField(max_length=255, blank=True, null=True)
    shipping_status = models.CharField(
        max_length=30,
        default="preparing",
        choices=[
            ("preparing", "배송 준비 중"),
            ("sending", "상품 발송"),
            ("delivery_company_arrives", "택배사 도착"),
            ("shipping", "배송 중"),
            ("delivered", "배송 완료"),
            ("canceled", "주문 취소"),
            ("returned", "반품 완료"),
        ],
    )
    shipping_memo = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"


# 상품 주문 내역 모델
class ProductOrder(models.Model):
    product_name = models.CharField(max_length=255)  # 상품 이름
    price = models.DecimalField(
        max_digits=10, decimal_places=2
    )  # 상품 구매 가격 (주문 당시)
    quantity = models.IntegerField()  # 상품 구매 갯수
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE
    )  # 주문내역 ID (Many-to-One 관계)
    discount_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00
    )
    product_id = models.IntegerField()
    product_company = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.quantity}x {self.product_name} for Order {self.order.id}"
