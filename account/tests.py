import pytest
import requests
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from account.models import User
from forcatProject.settings import KAKAO_CLIENT_ID


@pytest.fixture(scope="session")
def api_client():
    return APIClient()


class TestCase:
    def test_JWT_토큰_발급_테스트(self):
        user = User(username="username", nickname="nickname")
        access_token = AccessToken.for_user(user)
        assert access_token
