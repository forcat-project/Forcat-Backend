from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from account.api.serializer import UserSerializer
from account.models import User


class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(methods=["POST"], detail=False, url_path="sign-up")
    def sign_up(self, request):
        # 유저 생성 처리
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()  # 새 유저 생성

        # 유저를 위한 Access Token 생성
        access_token = AccessToken.for_user(user)

        # 응답 데이터에 토큰 추가
        response_data = serializer.data
        response_data["access_token"] = str(access_token)

        return Response(response_data, status=status.HTTP_201_CREATED)
