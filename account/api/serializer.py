import mimetypes
import uuid
from datetime import date

import boto3
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from account.models import User, Cat, CatBreed
from forcatProject import settings


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


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, file):
        # 이미지 파일 여부 확인 (MIME 타입 확인)
        mime_type, _ = mimetypes.guess_type(file.name)
        if not mime_type or not mime_type.startswith("image"):
            raise ValidationError("이미지 파일만 업로드할 수 있습니다.")
        return file

    def create(self, validated_data):
        file = validated_data["file"]

        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        url = "imgs/" + uuid.uuid1().hex

        s3_client.upload_fileobj(
            file,
            "forcat-bucket",
            url,
            ExtraArgs={"ContentType": file.content_type},
        )
        return {"file_url": f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{url}"}


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


class CatSerializer(serializers.ModelSerializer):
    days_since_birth = serializers.SerializerMethodField()
    cat_breed_name = serializers.SerializerMethodField(read_only=True)

    def get_cat_breed_name(self, obj):
        return obj.cat_breed.breed_type  # 출력 시 cat_breed의 name을 반환

    class Meta:
        model = Cat
        fields = [
            "name",
            "cat_breed",
            "cat_breed_name",
            "birth_date",
            "gender",
            "is_neutered",
            "weight",
            "profile_image",
            "days_since_birth",
        ]

    def get_days_since_birth(self, obj):
        if obj.birth_date:
            delta = date.today() - obj.birth_date
            return delta.days
        return None
