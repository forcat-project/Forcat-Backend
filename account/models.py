from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractBaseUser):
    username = models.CharField(max_length=50)
    nickname = models.CharField(max_length=50, unique=True)
    profile_picture = models.URLField(null=True)
    phone_number = models.CharField(max_length=50, null=True)
    address = models.TextField(null=True, blank=True)
    points = models.PositiveIntegerField(default=0)
    kakao_id = models.CharField(max_length=100, null=True, blank=True)
    naver_id = models.CharField(max_length=100, null=True, blank=True)
    google_id = models.CharField(max_length=100, null=True, blank=True)

    # USERNAME_FIELD을 username으로 설정
    USERNAME_FIELD = "nickname"
    REQUIRED_FIELDS = ["username"]  # 필수 필드 추가

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def is_anonymous(self) -> bool:
        return False

    def __str__(self):
        return self.username


# cat_breed 테이블
class CatBreed(models.Model):
    category_id = models.IntegerField(primary_key=True)
    breed_type = models.CharField(max_length=255, unique=True)
    rank = models.IntegerField(unique=True)

    class Meta:
        db_table = "cat_breed"

    def __str__(self):
        return self.breed_type


# cat 테이블
class Cat(models.Model):
    cat_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    cat_breed = models.ForeignKey(CatBreed, on_delete=models.CASCADE)
    birth_date = models.DateField()
    gender = models.IntegerField(
        choices=((0, "여아"), (1, "남아"))
    )  # 성별 (여아: 0, 남: 1)
    is_neutered = models.IntegerField(
        choices=((0, "안 했어요"), (1, "했어요"))
    )  # 중성화 여부 (했어요: 0, 안 했어요: 1)
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile_image = models.URLField(max_length=500, null=True, blank=True)

    class Meta:
        db_table = "cat"

    def __str__(self):
        return self.name
