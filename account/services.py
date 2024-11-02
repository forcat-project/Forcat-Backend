import random
import uuid

from django_redis import get_redis_connection


class PointService:
    cache = get_redis_connection("default")

    def get_random_point_hash(self) -> (str, int):
        value = self._get_random_point_value()
        if value == 0:
            return "", 0
        hash_key = uuid.uuid1().hex
        self.cache.set(hash_key, value, 300)
        return hash_key, value

    def is_available_hash(self, hash_key: str, point: int) -> bool:
        return int(self.cache.get(hash_key)) == point

    def delete_hashed_point(self, hash_key: str) -> None:
        self.cache.delete(hash_key)

    @staticmethod
    def _get_random_point_value():
        rand_val = random.random()  # 0 이상 1 미만의 난수 생성
        if rand_val < 1 / 500:
            return 5000
        elif rand_val < 1 / 100:
            return 1000
        elif rand_val < 1 / 50:
            return 500
        elif rand_val < 1 / 10:
            return 100
        elif rand_val < 1 / 2:  # 임시
            return 1
        return 0  # 어떤 조건에도 해당하지 않으면 0 반환
