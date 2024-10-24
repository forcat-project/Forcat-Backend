from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractBaseUser):
    username = models.CharField(max_length=50)
    nickname = models.CharField(max_length=50, unique=True)
    profile_picture = models.URLField(null=True)
    phone_number = models.CharField(max_length=50, null=True)
    address = models.TextField(null=True, blank=True)
    address_detail = models.TextField(null=True, blank=True)
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
