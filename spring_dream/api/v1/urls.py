from django.urls import path

from api.v1.views.auth import CustomOAuth2Token


urlpatterns = [
    path('api-token-auth/', CustomOAuth2Token.as_view()),
]