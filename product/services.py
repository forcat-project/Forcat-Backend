from typing import Optional

from django_redis import get_redis_connection


class ProductService:
    PRODUCT_SEARCH_KEY = "product_search_count"
    cache = get_redis_connection("default")

    def increase_search_count(self, search_keyword: Optional[str]) -> None:
        """
        검색어로 카운트를 증가시킴
        """
        if search_keyword:
            self.cache.zincrby(self.PRODUCT_SEARCH_KEY, 1, search_keyword)

    def get_top_keywords(self, limit: int) -> list[dict[str:int]]:
        """
        검색 카운트 기준으로 정렬하여 상위 상품 반환
        """
        product_scores = {}
        for keyword, score in self.cache.zrange(
            self.PRODUCT_SEARCH_KEY, 0, -1, withscores=True
        ):
            product_scores[keyword] = score
        return sorted(product_scores.items(), key=lambda x: x[1], reverse=True)[:limit]
