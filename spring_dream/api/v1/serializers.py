from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework.validators import UniqueValidator


class UserCreateSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        max_length=200,
        write_only=True,
        required=True
    )
    is_active = serializers.BooleanField(read_only=True, default=False)
    email = serializers.EmailField(validators=[UniqueValidator(queryset=get_user_model().objects.all())])

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'first_name', 'last_name', 'is_active', ]



class UserPartialSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = [
            'id',
            'first_name',
            'is_active',
            'is_staff',
            'last_login',
        ]


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        read_only=True
    )
    password = serializers.CharField(
        max_length=200,
        write_only=True,
    )
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    is_staff = serializers.BooleanField(read_only=True)
    last_login = serializers.DateTimeField(read_only=True)
    is_active = serializers.BooleanField()

    class Meta:
        model = get_user_model()
        fields = [
            'email',
            'password',
            'first_name',
            'last_name',
            'is_active',
            'is_staff',
            'last_login',
        ]


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(
        write_only=True
    )
    password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )
    token = serializers.CharField(
        read_only=True
    )

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                username=email, password=password)
            if not user:
                msg = 'Unable to log in with provided credentials.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Must include "email" and "password".'
            raise serializers.ValidationError(msg, code='authorization')

        data['user'] = user
        return data