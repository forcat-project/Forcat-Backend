from django.shortcuts import redirect
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken
import requests


from account.models import User
from forcatProject.settings import (
    FRONT_END_ENDPOINT,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_REDIRECT_URI,
)


class GoogleOauthViewSet(APIView):
    def get(self, request):
        code = self._get_code_from_request(request)
        if not code:
            return Response(
                {"error": "Missing code parameter"}, status=status.HTTP_400_BAD_REQUEST
            )

        access_token = self._get_access_token(code)
        if not access_token:
            return Response(
                {"error": "Failed to get access token from Google"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_info = self._get_user_info(access_token)
        if not user_info:
            return Response(
                {"error": "Failed to get user info from Google"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if self._is_user_exists(user_info["sub"]):
            auth_token = self._get_auth_token(user_info["sub"])
            return redirect(f"{FRONT_END_ENDPOINT}?token={auth_token}")

        return redirect(
            f'{FRONT_END_ENDPOINT}?id={user_info["sub"]}&name={user_info["name"]}&picture={user_info["picture"]}'
        )

    def _get_code_from_request(self, request) -> str:
        """
        요청에서 'code' 쿼리 파라미터를 추출합니다.
        """
        return request.GET.get("code")

    def _get_access_token(self, code: str) -> str:
        """
        Google API를 사용하여 액세스 토큰을 얻습니다.
        """
        token_url = "https://oauth2.googleapis.com/token"

        data = {
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }

        try:
            response = requests.post(token_url, data=data)

            response.raise_for_status()
            token_data = response.json()
            return token_data.get("access_token")
        except requests.exceptions.RequestException as e:
            print(f"Error getting access token: {str(e)}")
            return None

    def _get_user_info(self, access_token: str) -> dict:
        """
        액세스 토큰을 사용하여 Google API에서 사용자 정보를 가져옵니다.
        """
        user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}

        try:
            response = requests.get(user_info_url, headers=headers)
            response.raise_for_status()

            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting user info: {str(e)}")
            return None

    def _is_user_exists(self, google_id: str) -> bool:
        """
        주어진 google_id로 사용자가 존재하는지 확인합니다.
        """
        return User.objects.filter(google_id=google_id).exists()

    def _get_auth_token(self, google_id: str) -> str:
        """
        우리 서버의 auth token을 User의 정보로 가져옵니다.
        """
        user = User.objects.get(google_id=google_id)
        access_token = AccessToken.for_user(user)
        return str(access_token)
