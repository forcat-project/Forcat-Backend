import pytest
from django.test import TestCase


@pytest.mark.django_db
class ProductViewSetTest(TestCase):
    def setUp(self):
        ...

    def make_user_info(self):
        ...

    def test_상품_조회_테스트(self):
        ...
