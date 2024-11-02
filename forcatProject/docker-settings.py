from .settings import *

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/1",  # 'redis_boot' 대신 'redis'로 설정
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}


# 환경 변수로부터 환경 값을 가져오기
ENVIRONMENT = os.getenv("ENVIRONMENT")

# production 환경에서만 프록시 헤더 설정 적용
if ENVIRONMENT == "production":
    USE_X_FORWARDED_HOST = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
