import pytest
import requests
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from account.models import User
from forcatProject.settings import KAKAO_CLIENT_ID


@pytest.fixture(scope="session")
def api_client():
    return APIClient()


@pytest.fixture()
def 테스트_카카오_가입_유저_생성():
    User.objects.create(
        username="카카오_유저",
        nickname="카카오_닉네임",
        profile_picture="http://kakao.com",
        phone_number="010-0000-1000",
        address="카카오_사옥",
        address_detail="201호",
        kakao_id="kakao",
    )


@pytest.mark.django_db
class TestCase:
    def test_JWT_토큰_발급_테스트(self):
        user = User(username="username", nickname="nickname")
        access_token = AccessToken.for_user(user)
        assert access_token

    def test_유저_기본_회원가입_테스트(self, api_client):
        url = "/api/users/sign-up"

        res = api_client.post(
            url,
            data={
                "username": "김_유저네임",
                "nickname": "김_닉네임",
                "profile_picture": "http://www.naver.com",
                "phone_number": "010-0000-0000",
                "address": "김둥둥둥",
                "address_detail": "김바바바",
            },
        )

        assert res.json()["access_token"] != ""
