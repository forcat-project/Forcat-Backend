import uuid

import pytest
from django_redis import get_redis_connection
from freezegun import freeze_time
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken
from django.urls import reverse
from account.models import Cat, CatBreed, User, Point


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


@pytest.fixture
def 사용자_생성():
    return User.objects.create(
        username="testuser",
        nickname="testnickname",
        profile_picture="http://example.com/profile.jpg",
        phone_number="010-1234-5678",
        address="123 Main St, City, Country",
        kakao_id="kakao123",
        naver_id="naver123",
        google_id="google123",
    )


@pytest.fixture
def 고양이_품종_생성():
    return CatBreed.objects.create(category_id=1, breed_type="Persian", rank=1)


@pytest.fixture
def 고양이_생성(사용자_생성, 고양이_품종_생성):
    def _여러_고양이_생성():
        return [
            Cat.objects.create(
                name="Kitty1",
                cat_breed=고양이_품종_생성,
                birth_date="2020-01-01",
                gender=1,
                is_neutered=1,
                weight=4.50,
                user=사용자_생성,
                profile_image="http://example.com/profile1.jpg",
            ),
            Cat.objects.create(
                name="Kitty2",
                cat_breed=고양이_품종_생성,
                birth_date="2019-06-15",
                gender=0,
                is_neutered=0,
                weight=5.00,
                user=사용자_생성,
                profile_image="http://example.com/profile2.jpg",
            ),
            Cat.objects.create(
                name="Kitty3",
                cat_breed=고양이_품종_생성,
                birth_date="2018-08-25",
                gender=1,
                is_neutered=1,
                weight=3.80,
                user=사용자_생성,
                profile_image="http://example.com/profile3.jpg",
            ),
        ]

    return _여러_고양이_생성


@pytest.fixture
def 포인트_생성(사용자_생성):
    Point.objects.create(point_id="1", user=사용자_생성, point=100)
    Point.objects.create(point_id="2", user=사용자_생성, point=500)
    Point.objects.create(point_id="3", user=사용자_생성, point=1000)
    Point.objects.create(point_id="4", user=사용자_생성, point=5000)


class TestJWTToken:
    def test_JWT_토큰_발급_테스트(self):
        user = User(username="username", nickname="nickname")
        access_token = AccessToken.for_user(user)
        assert access_token


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

    def test_유저_조회_테스트(self, api_client, 테스트_카카오_가입_유저_생성):
        url = reverse("user-detail", kwargs={"pk": 1})

        res = api_client.get(url)

        assert res.json() == {
            "id": 1,
            "username": "카카오_유저",
            "nickname": "카카오_닉네임",
            "points": 0,
            "profile_picture": "http://kakao.com",
            "phone_number": "010-0000-1000",
            "address": "카카오_사옥",
            "address_detail": "201호",
        }

    def test_유저_수정_테스트(self, api_client, 테스트_카카오_가입_유저_생성):
        url = reverse("user-detail", kwargs={"pk": 1})

        res = api_client.patch(
            url, data={"username": "네이버_유저", "nickname": "네이버_닉네임"}
        )

        assert res.json() == {
            "username": "네이버_유저",
            "nickname": "네이버_닉네임",
            "profile_picture": "http://kakao.com",
            "phone_number": "010-0000-1000",
            "address": "카카오_사옥",
            "address_detail": "201호",
        }

    def test_유저_수정_실패_테스트(self, api_client, 테스트_카카오_가입_유저_생성):
        url = reverse("user-detail", kwargs={"pk": 1})

        api_client.patch(url, data={"kakao_id": "naver"})

        assert User.objects.filter(kakao_id="kakao").exists() is True
        assert User.objects.filter(kakao_id="naver").exists() is False


@pytest.mark.django_db
class TestCatCRUD:
    @freeze_time("2024-10-24")
    def test_고양이_생성_테스트(self, api_client, 사용자_생성, 고양이_품종_생성):
        api_client.force_authenticate(user=사용자_생성)
        url = reverse("user-cats", kwargs={"user_id": 사용자_생성.id})
        data = {
            "name": "NewCat",
            "cat_breed": 고양이_품종_생성.category_id,
            "birth_date": "2021-05-20",
            "gender": 0,
            "is_neutered": 1,
            "weight": 3.20,
            "profile_image": "http://example.com/newcat.jpg",
        }

        response = api_client.post(url, data, format="json")
        assert response.status_code == 201
        assert response.json() == {
            "name": "NewCat",
            "cat_breed": 1,
            "cat_breed_name": "Persian",
            "birth_date": "2021-05-20",
            "gender": 0,
            "is_neutered": 1,
            "weight": "3.20",
            "profile_image": "http://example.com/newcat.jpg",
            "days_since_birth": 1253,
        }

    @freeze_time("2024-10-24")
    def test_고양이_목록_조회_테스트(self, api_client, 고양이_생성):
        고양이_생성()
        url = reverse("user-cats", kwargs={"user_id": 1})
        response = api_client.get(url)

        assert response.status_code == 200
        assert response.json() == [
            {
                "name": "Kitty1",
                "cat_breed": 1,
                "cat_breed_name": "Persian",
                "birth_date": "2020-01-01",
                "gender": 1,
                "is_neutered": 1,
                "weight": "4.50",
                "profile_image": "http://example.com/profile1.jpg",
                "days_since_birth": 1758,
            },
            {
                "name": "Kitty2",
                "cat_breed": 1,
                "cat_breed_name": "Persian",
                "birth_date": "2019-06-15",
                "gender": 0,
                "is_neutered": 0,
                "weight": "5.00",
                "profile_image": "http://example.com/profile2.jpg",
                "days_since_birth": 1958,
            },
            {
                "name": "Kitty3",
                "cat_breed": 1,
                "cat_breed_name": "Persian",
                "birth_date": "2018-08-25",
                "gender": 1,
                "is_neutered": 1,
                "weight": "3.80",
                "profile_image": "http://example.com/profile3.jpg",
                "days_since_birth": 2252,
            },
        ]

    @freeze_time("2024-10-24")
    def test_고양이_업데이트_테스트(self, api_client, 사용자_생성, 고양이_생성):
        api_client.force_authenticate(user=사용자_생성)
        cats = 고양이_생성()
        cat_to_update = cats[0]
        url = reverse(
            "user-cat-detail",
            kwargs={"user_id": 사용자_생성.id, "cat_id": cat_to_update.cat_id},
        )

        data = {
            "name": "UpdatedCat",
            "cat_breed": 1,
            "cat_breed_name": "Persian",
            "birth_date": "2020-01-01",
            "gender": 1,
            "is_neutered": 1,
            "weight": 5.00,
            "profile_image": "http://example.com/updated_image.jpg",  # 이미지 URL로 수정
        }

        response = api_client.put(url, data, format="json")

        assert response.status_code == 200
        assert response.json() == {
            "name": "UpdatedCat",
            "cat_breed": 1,
            "cat_breed_name": "Persian",
            "birth_date": "2020-01-01",
            "gender": 1,
            "is_neutered": 1,
            "weight": "5.00",
            "profile_image": "http://example.com/updated_image.jpg",
            "days_since_birth": 1758,
        }

    def test_고양이_삭제_테스트(self, api_client, 사용자_생성, 고양이_생성):
        api_client.force_authenticate(user=사용자_생성)

        cats = 고양이_생성()
        cat_to_delete = cats[0]
        url = reverse(
            "user-cat-detail",
            kwargs={"user_id": 사용자_생성.id, "cat_id": cat_to_delete.cat_id},
        )
        response = api_client.delete(url)
        assert response.status_code == 204
        assert Cat.objects.count() == 2

        with pytest.raises(Cat.DoesNotExist):
            Cat.objects.get(cat_id=cat_to_delete.cat_id)


@pytest.mark.django_db
class TestPoint:
    def test_포인트를_가진_사용자_조회(self, api_client, 사용자_생성, 포인트_생성):
        url = reverse("user-detail", kwargs={"pk": 사용자_생성.id})

        res = api_client.get(url)

        assert res.json() == {
            "id": 1,
            "username": "testuser",
            "nickname": "testnickname",
            "profile_picture": "http://example.com/profile.jpg",
            "phone_number": "010-1234-5678",
            "address": "123 Main St, City, Country",
            "address_detail": None,
            "points": 6600,
        }

    def test_랜덤_포인트_생성(self, api_client, 사용자_생성):
        redis_cache = get_redis_connection("default")
        hash_key = uuid.uuid1().hex
        value = 100
        redis_cache.set(hash_key, value, 300)
