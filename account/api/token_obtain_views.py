from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers


class TokenRefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(required=True)


class CustomTokenRefreshView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = TokenRefreshSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        refresh = serializer.validated_data["refresh_token"]

        # 새로운 Access Token 생성
        access_token = str(refresh.access_token)

        return Response(
            {"access_token": access_token, "refresh_token": str(refresh)},
            status=status.HTTP_200_OK,
        )
