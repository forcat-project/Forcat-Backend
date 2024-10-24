from rest_framework import serializers

from account.models import User


class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    kakao_id = serializers.CharField(write_only=True, allow_null=True, required=False)
    naver_id = serializers.CharField(write_only=True, allow_null=True, required=False)
    google_id = serializers.CharField(write_only=True, allow_null=True, required=False)

    class Meta:
        model = User
        fields = [
            "id",
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


class UserUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "username",
            "nickname",
            "profile_picture",
            "phone_number",
            "address",
            "address_detail",
        ]
