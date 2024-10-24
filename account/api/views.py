from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from account.api.serializer import UserSerializer, UserUpdateSerializer
from account.models import User


class UserViewSet(
    viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin
):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    default_serializer_class = UserSerializer  # 기본 직렬화기
    update_serializer_class = UserUpdateSerializer  # 업데이트에 사용할 직렬화기

    def get_serializer_class(self):
        # 'update', 'partial_update' 요청일 때 다른 serializer 사용
        if self.action in ["update", "partial_update"]:
            return self.update_serializer_class
        return self.default_serializer_class

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
