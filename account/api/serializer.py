import mimetypes
import uuid

import boto3
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from account.models import User
from forcatProject import settings


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
