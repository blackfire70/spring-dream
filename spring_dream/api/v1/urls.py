from django.urls import path

from rest_framework.routers import DefaultRouter

from api.v1.views.auth import CustomOAuth2Token
from api.v1.views.users import UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)


urlpatterns = [
    path('api-token-auth/', CustomOAuth2Token.as_view()),
] + router.urls