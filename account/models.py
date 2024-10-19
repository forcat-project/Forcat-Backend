from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    date_of_birth = models.DateField(null=True, blank=True)
    nickname = models.CharField(max_length=50, unique=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    points = models.PositiveIntegerField(default=0)
    address = models.TextField(null=True, blank=True)
    kakao_id = models.CharField(max_length=100, null=True, blank=True)
    naver_id = models.CharField(max_length=100, null=True, blank=True)
    google_id = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.username
