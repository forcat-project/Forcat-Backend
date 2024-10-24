from rest_framework import serializers

from account.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "username",
            "nickname",
            "profile_picture",
            "phone_number",
            "address",
            "address_detail",
            "kakao_id",
            "naver_id",
            "google_id",
        ]
