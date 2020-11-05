from oauth2_provider.models import AccessToken
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response

from api.v1.serializers import LoginSerializer

class CustomOAuth2Token(ObtainAuthToken):

    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = AccessToken.objects.get_or_create(user=user)
        return Response({
            'token': token.token,
        })