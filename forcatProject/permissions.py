from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.authentication import JWTAuthentication


class IsAuthenticatedWithJWT(BasePermission):
    def has_permission(self, request, view):
        try:
            JWTAuthentication().authenticate(request)
            return True
        except Exception:
            return False


class IsUserMatching(BasePermission):
    def has_permission(self, request, view):
        # JWT 토큰을 통해 사용자 정보 가져오기
        try:
            user, _ = JWTAuthentication().authenticate(request)
        except Exception as e:
            print(e)
            return False

        # URL에서 user_id를 가져와서 비교
        user_id = view.kwargs.get("pk") or view.kwargs.get("user_id")
        return user_id is not None and str(user.id) == str(user_id)
