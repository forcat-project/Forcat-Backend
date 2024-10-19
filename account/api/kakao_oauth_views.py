from typing import Optional

import requests
from django.shortcuts import redirect

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from forcatProject.settings import KAKAO_REDIRECT_URI, KAKAO_CLIENT_ID, KAKAO_CLIENT_SECRET, FRONT_END_ENDPOINT


class KakaoOauthViewSet(APIView):
    KAKAO_GRANT_TYPE = 'authorization_code'
    KAKAO_TOKEN_URL = 'https://kauth.kakao.com/oauth/token'
    KAKAO_USER_INFO_URL = 'https://kapi.kakao.com/v2/user/me'

    def get(self, request):
        code = self._get_code_from_request(request)
        if not code:
            return Response({"error": "Missing code parameter"}, status=status.HTTP_400_BAD_REQUEST)

        access_token = self._get_access_token(code)
        if not access_token:
            return Response({"error": "Failed to get access token from Kakao"}, status=status.HTTP_400_BAD_REQUEST)

        user_info = self._get_user_info(access_token)
        if not user_info:
            return Response({"error": "Failed to get user info from Kakao"}, status=status.HTTP_400_BAD_REQUEST)

        if self._is_user_exists(user_info["id"]):
            auth_token = self._get_auth_token(user_info["id"])
            return redirect(f"{FRONT_END_ENDPOINT}?token={auth_token}")
        return redirect(f'{FRONT_END_ENDPOINT}?id={user_info["id"]}&nickname={user_info["properties"]["nickname"]}&profile_image=${user_info["properties"]["nickname"]}&')

    def _get_code_from_request(self, request) -> str:
        """
        요청에서 'code' 쿼리 파라미터를 추출합니다.
        """
        return request.query_params.get('code')

    def _get_access_token(self, code) -> Optional[str]:
        """
        Kakao API를 사용하여 액세스 토큰을 얻습니다.
        """
        token_response = requests.post(self.KAKAO_TOKEN_URL, data={
            'grant_type': self.KAKAO_GRANT_TYPE,
            'client_id': KAKAO_CLIENT_ID,
            'redirect_uri': KAKAO_REDIRECT_URI,
            'code': code,
            'client_secret': KAKAO_CLIENT_SECRET
        })

        if token_response.status_code != 200:
            return None

        token_data = token_response.json()
        return token_data.get('access_token')

    def _get_user_info(self, access_token):
        """
        액세스 토큰을 사용하여 Kakao API에서 사용자 정보를 가져옵니다.
        """
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        user_info_response = requests.get(self.KAKAO_USER_INFO_URL, headers=headers)

        if user_info_response.status_code != 200:
            return None

        return user_info_response.json()

    def _is_user_exists(self, kakao_id: str) -> bool:
        """
        kakao_id로 이미 가입한 유저가 존재하는지 확인합니다.
        """
        pass

    def _get_auth_token(self, kakao_id: str) -> bool:
        """
        우리 서버의 auth token을 User의 정보로 가져옵니다.
        """
        pass
