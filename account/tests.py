import pytest
import requests
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken
from django.urls import reverse
from account.models import Cat, CatBreed, User

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


@pytest.fixture
def user(db):
    # Custom User 모델에 맞춘 유저 생성
    return User.objects.create(
        username='testuser',
        nickname='testnickname',
        profile_picture='http://example.com/profile.jpg',
        phone_number='010-1234-5678',
        address='123 Main St, City, Country',
        points=100,
        kakao_id='kakao123',
        naver_id='naver123',
        google_id='google123'
    )


@pytest.fixture
def cat_breed(db):
    # 고양이 묘종 생성
    return CatBreed.objects.create(category_id=1, breed_type='Persian', rank=1)


@pytest.fixture
def cat(db, user, cat_breed):
    # 고양이 데이터 생성
    return Cat.objects.create(
        name='Kitty',
        cat_breed=cat_breed,
        birth_date='2020-01-01',
        gender=1,
        is_neutered=1,
        weight=4.50,
        user=user
    )


def test_create_cat(api_client, user, cat_breed):
    # 고양이 생성 테스트
    api_client.force_authenticate(user=user)
    url = reverse('cat-list')  # router에 등록된 'cats' URL reverse
    data = {
        'name': 'NewCat',
        'cat_breed': cat_breed.category_id,
        'birth_date': '2021-05-20',
        'gender': 0,
        'is_neutered': 1,
        'weight': 3.20,
        'user': user.id
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == 201
    assert response.data['name'] == 'NewCat'


def test_get_cat(api_client, cat):
    # 고양이 목록 조회 테스트
    url = reverse('cat-list')
    response = api_client.get(url)
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['name'] == cat.name


def test_update_cat(api_client, user, cat):
    # 고양이 업데이트 테스트
    api_client.force_authenticate(user=user)
    url = reverse('cat-detail', args=[cat.cat_id])
    data = {
        'name': 'UpdatedCat',
        'cat_breed': cat.cat_breed.category_id,
        'birth_date': '2020-01-01',
        'gender': 1,
        'is_neutered': 1,
        'weight': 5.00,
        'user': user.id
    }
    response = api_client.put(url, data, format='json')
    assert response.status_code == 200
    assert response.data['name'] == 'UpdatedCat'
    assert response.data['weight'] == '5.00'


def test_delete_cat(api_client, user, cat):
    # 고양이 삭제 테스트
    api_client.force_authenticate(user=user)
    url = reverse('cat-detail', args=[cat.cat_id])
    response = api_client.delete(url)
    assert response.status_code == 204
    assert Cat.objects.count() == 0