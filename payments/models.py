from django.db import models
from django.contrib.auth.models import User


# 주문 모델
class Order(models.Model):
    id = models.AutoField(primary_key=True)  # 구매내역 ID
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 유저 ID
    payment = models.OneToOneField(
        "Payment", on_delete=models.SET_NULL, null=True
    )  # 결제 TX ID (1:1 관계)
    products = models.ManyToManyField(
        "ProductOrder"
    )  # 구매 상품 내역 IDS (Many-to-Many 관계)
    order_date = models.DateTimeField(auto_now_add=True)  # 구매 일자
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)  # 총 결제 금액
    payment_method = models.CharField(
        max_length=20,
        choices=[
            ("card", "카드"),
            ("bank", "계좌이체"),
            ("point", "포인트"),
            ("other", "기타"),
        ],
    )  # 결제 방법
    shipping_address = models.CharField(max_length=255)  # 배송지 주소
    shipping_status = models.CharField(
        max_length=20,
        default="preparing",
        choices=[
            ("preparing", "배송 준비 중"),
            ("shipping", "배송 중"),
            ("delivered", "배송 완료"),
        ],
    )  # 배송 상태
    points_used = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )  # 포인트 사용 금액

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"


# 결제 모델
class Payment(models.Model):
    id = models.AutoField(primary_key=True)  # 결제 TX ID
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # 결제 금액
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 결제 유저 ID (참조)
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
        return f"Payment {self.id} for {self.user.username}"


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

    def __str__(self):
        return f"{self.quantity}x {self.product_name} for Order {self.order.id}"
