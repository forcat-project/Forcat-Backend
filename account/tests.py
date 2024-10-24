import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken
from django.urls import reverse
from account.models import Cat, CatBreed, User
from django.core.files.uploadedfile import SimpleUploadedFile


@pytest.fixture(scope="session")
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create(
        username="testuser",
        nickname="testnickname",
        profile_picture="http://example.com/profile.jpg",
        phone_number="010-1234-5678",
        address="123 Main St, City, Country",
        points=100,
        kakao_id="kakao123",
        naver_id="naver123",
        google_id="google123",
    )


@pytest.fixture
def cat_breed(db):
    return CatBreed.objects.create(category_id=1, breed_type="Persian", rank=1)


@pytest.fixture
def 고양이_생성(db, user, cat_breed):
    def _여러_고양이_생성():
        return [
            Cat.objects.create(
                name="Kitty1",
                cat_breed=cat_breed,
                birth_date="2020-01-01",
                gender=1,
                is_neutered=1,
                weight=4.50,
                user=user,
                profile_image="http://example.com/profile1.jpg",
            ),
            Cat.objects.create(
                name="Kitty2",
                cat_breed=cat_breed,
                birth_date="2019-06-15",
                gender=0,
                is_neutered=0,
                weight=5.00,
                user=user,
                profile_image="http://example.com/profile2.jpg",
            ),
            Cat.objects.create(
                name="Kitty3",
                cat_breed=cat_breed,
                birth_date="2018-08-25",
                gender=1,
                is_neutered=1,
                weight=3.80,
                user=user,
                profile_image="http://example.com/profile3.jpg",
            ),
        ]

    return _여러_고양이_생성


class TestJWTToken:
    def test_JWT_토큰_발급_테스트(self):
        user = User(username="username", nickname="nickname")
        access_token = AccessToken.for_user(user)
        assert access_token


class TestCatCRUD:
    def test_고양이_생성_테스트(self, api_client, user, cat_breed):
        api_client.force_authenticate(user=user)
        url = reverse("cat-list")
        data = {
            "name": "NewCat",
            "cat_breed": cat_breed.category_id,
            "birth_date": "2021-05-20",
            "gender": 0,
            "is_neutered": 1,
            "weight": 3.20,
            "user": user.id,
            "profile_image": "http://example.com/newcat.jpg",
        }

        response = api_client.post(url, data, format="json")
        assert response.status_code == 201
        assert response.json() == {
            "name": "NewCat",
            "cat_breed": 1,
            "birth_date": "2021-05-20",
            "gender": 0,
            "is_neutered": 1,
            "weight": "3.20",
            "user": 1,
            "profile_image": "http://example.com/newcat.jpg",
            "days_since_birth": 1253,
        }

    def test_고양이_목록_조회_테스트(self, api_client, 고양이_생성):
        고양이_생성()
        url = reverse("cat-list")
        response = api_client.get(url)

        assert response.status_code == 200
        assert response.json() == [
            {
                "name": "Kitty1",
                "cat_breed": 1,
                "birth_date": "2020-01-01",
                "gender": 1,
                "is_neutered": 1,
                "weight": "4.50",
                "user": 1,
                "profile_image": "http://example.com/profile1.jpg",
                "days_since_birth": 1758,
            },
            {
                "name": "Kitty2",
                "cat_breed": 1,
                "birth_date": "2019-06-15",
                "gender": 0,
                "is_neutered": 0,
                "weight": "5.00",
                "user": 1,
                "profile_image": "http://example.com/profile2.jpg",
                "days_since_birth": 1958,
            },
            {
                "name": "Kitty3",
                "cat_breed": 1,
                "birth_date": "2018-08-25",
                "gender": 1,
                "is_neutered": 1,
                "weight": "3.80",
                "user": 1,
                "profile_image": "http://example.com/profile3.jpg",
                "days_since_birth": 2252,
            },
        ]

    def test_고양이_업데이트_테스트(self, api_client, user, 고양이_생성):
        api_client.force_authenticate(user=user)
        cats = 고양이_생성()
        cat_to_update = cats[0]
        url = reverse("cat-detail", args=[cat_to_update.cat_id])

        data = {
            "name": "UpdatedCat",
            "cat_breed": cat_to_update.cat_breed.category_id,
            "birth_date": "2020-01-01",
            "gender": 1,
            "is_neutered": 1,
            "weight": 5.00,
            "user": user.id,
            "profile_image": "http://example.com/updated_image.jpg",  # 이미지 URL로 수정
        }

        response = api_client.put(url, data, format="json")

        assert response.status_code == 200
        assert response.json() == {
            "name": "UpdatedCat",
            "cat_breed": 1,
            "birth_date": "2020-01-01",
            "gender": 1,
            "is_neutered": 1,
            "weight": "5.00",
            "user": 1,
            "profile_image": "http://example.com/updated_image.jpg",
            "days_since_birth": 1758,
        }

    def test_고양이_삭제_테스트(self, api_client, user, 고양이_생성):
        api_client.force_authenticate(user=user)

        cats = 고양이_생성()
        cat_to_delete = cats[0]
        url = reverse("cat-detail", args=[cat_to_delete.cat_id])
        response = api_client.delete(url)
        assert response.status_code == 204
        assert Cat.objects.count() == 2

        with pytest.raises(Cat.DoesNotExist):
            Cat.objects.get(cat_id=cat_to_delete.cat_id)
