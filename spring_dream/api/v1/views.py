from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.validators import ValidationError
from django.db import transaction

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from api.v1.serializers import (
    UserSerializer,
    UserIncompleteSerializer,
    UserLoginSerializer,
    UserCreateSerializer,
)
from core.utils import send_activation_mail
from core.utils import create_application, create_token
from oauth2_provider.models import AccessToken


class UserViewSet(viewsets.ModelViewSet):
    '''
    User ViewSet
    Contains all the operations to the model User
    '''

    model = User
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]

    def list(self, request):
        '''
        Resource:
        api/v1/users/
        Only authenticated users can see email field
        as well as last name field.
        '''
        if request.auth:
            serializer = self.get_serializer(self.queryset, many=True)
        else:
            serializer = UserIncompleteSerializer(self.queryset, many=True)

        return Response(serializer.data)

    @action(
        detail=False,
        methods=['patch'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def change_password(self, request):
        '''
        Resource:
        api/v1/users/change_password/
        '''
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            user.set_password(request.data['password'])
            user.save()
            return Response(
                {'message': 'password changed.'},
                status.HTTP_200_OK
            )
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def signup(self, request):
        '''
        Resource:
        api/v1/users/signup/
        Creates inactive user instance and
        sends an activation email to the user.
        '''

        serializer = UserCreateSerializer(data=request.data)

        if serializer.is_valid():
            user = User(
                first_name=serializer.data.get('first_name') or '',
                last_name=serializer.data.get('last_name') or '',
                email=serializer.data['email'],
                username=serializer.data['email'],
                is_active=False
            )

            user.set_password(request.data['password'])
            try:
                user.full_clean()
            except ValidationError as e:
                return Response(
                    {'error': 'cause:{}'.format(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                user.save()
                app = create_application(user)
                create_token(user, app)
                # TO DO: convert mail sending to a celery task
                send_activation_mail(user=user)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def activate(self, request, pk=None):
        '''
        Resource:
        api/v1/users/<pk>/activate/
        Sets the user's is_active = True after validation of the token
        '''
        if not request.auth:
            return Response(
                {'message': 'invalid token'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        user = request.user
        user.is_active = True
        user.save()
        return Response(
            {'message': 'account activated'},
            status=status.HTTP_200_OK
        )

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