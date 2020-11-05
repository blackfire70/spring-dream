from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db import transaction

from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from oauth2_provider.models import AccessToken

from api.v1.serializers import UserCreateSerializer
from api.v1.serializers import UserLoginSerializer
from api.v1.serializers import UserPartialSerializer
from api.v1.serializers import UserSerializer
from core.permissions import IsOwnerOrReadOnly
from core.utils import create_application
from core.utils import create_token
from core.utils import send_activation_mail


class UserViewSet(viewsets.ModelViewSet):
    """
    User ViewSet
    Contains all the operations to the model User
    """

    model = User
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsOwnerOrReadOnly, ]

    def get_serializer_class(self):
        """
        Returns a different serializer depending
        if the user is authenticated or not
        """
        if self.request.auth and self.request.user.is_active:
            serializer = self.serializer_class
        else:
            serializer = UserPartialSerializer

        return serializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def perform_create(self, serializer):
        # Populate username field with email
        serializer.validated_data['username'] = serializer.validated_data[
            'email']
        serializer.validated_data['is_active'] = False
        serializer.save()
        # Create app and access token for the user
        user = serializer.instance
        user.set_password(serializer.initial_data['password'])
        app = create_application(user)
        create_token(user, app)
        transaction.on_commit(lambda: send_activation_mail(user=user))

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def perform_update(self, serializer):
        """
        Support password change on PATCH
        """
        password = serializer.initial_data.get('password')
        if password:
            serializer.instance.set_password(password)
        return super().perform_create(serializer)

    @action(detail=False, methods=['post'])
    def login(self, request):
        '''
        Resource:
        api/v1/users/login/
        User login. After authentication, the user is logged in and
        a bearer token is given.
        '''
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.data['email'],
                password=request.data['password']
            )
            if user:
                token = AccessToken.objects.get(user=user).token
                return Response({'token': token}, status=status.HTTP_200_OK)
            return Response(
                {'message': 'Invalid email/password or inactive account'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
