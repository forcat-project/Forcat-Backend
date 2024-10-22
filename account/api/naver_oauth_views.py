from typing import Optional

import requests
from django.shortcuts import redirect

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from account.models import User
from forcatProject.settings import (
    NAVER_REDIRECT_URI,
    NAVER_CLIENT_ID,
    NAVER_CLIENT_SECRET,
    FRONT_END_ENDPOINT,
)


class NaverOauthViewSet(APIView):
    NAVER_GRANT_TYPE = "authorization_code"
    NAVER_TOKEN_URL = "https://nid.naver.com/oauth2.0/token"
    NAVER_USER_INFO_URL = "https://openapi.naver.com/v1/nid/me"

    def get(self, request):
        code = self._get_code_from_request(request)
        if not code:
            return Response(
                {"error": "Missing code parameter"}, status=status.HTTP_400_BAD_REQUEST
            )

        access_token = self._get_access_token(code)

        if not access_token:
            return Response(
                {"error": "Failed to get access token from Naver"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user_info = self._get_user_info(access_token)

        if not user_info:
            return Response(
                {"error": "Failed to get user info from Naver"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if self._is_user_exists(user_info["response"]["id"]):
            auth_token = self._get_auth_token(user_info["response"]["id"])
            return redirect(f"{FRONT_END_ENDPOINT}?token={auth_token}")
        return redirect(
            f'{FRONT_END_ENDPOINT}?id={user_info["response"]["id"]}&nickname={user_info["response"]["nickname"]}&profile_image={user_info["response"]["profile_image"]}&'
        )

    def _get_code_from_request(self, request) -> str:
        """
        요청에서 'code' 쿼리 파라미터를 추출합니다.
        """
        return request.query_params.get("code")

    def _get_access_token(self, code) -> Optional[str]:
        """
        Naver API를 사용하여 액세스 토큰을 얻습니다.
        """
        token_response = requests.post(
            self.NAVER_TOKEN_URL,
            params={
                "grant_type": self.NAVER_GRANT_TYPE,
                "client_id": NAVER_CLIENT_ID,
                "client_secret": NAVER_CLIENT_SECRET,
                "code": code,
                "redirect_uri": NAVER_REDIRECT_URI,
            },
        )

        if token_response.status_code != 200:
            return None

        token_data = token_response.json()
        return token_data.get("access_token")

    def _get_user_info(self, access_token):
        """
        액세스 토큰을 사용하여 Naver API에서 사용자 정보를 가져옵니다.
        """
        headers = {"Authorization": f"Bearer {access_token}"}
        user_info_response = requests.get(self.NAVER_USER_INFO_URL, headers=headers)

        if user_info_response.status_code != 200:
            return None

        return user_info_response.json()

    def _is_user_exists(self, naver_id: str) -> bool:
        """
        naver_id로 이미 가입한 유저가 존재하는지 확인합니다.
        """
        return User.objects.filter(naver_id=naver_id).exists()

    def _get_auth_token(self, naver_id: str) -> str:
        """
        우리 서버의 auth token을 User의 정보로 가져옵니다.
        """
        user = User.objects.filter.get(naver_id=naver_id)
        access_token = AccessToken.for_user(user)
        return access_token.__str__()
