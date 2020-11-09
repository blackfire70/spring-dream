from django.conf import settings
from django.utils import timezone

from oauth2_provider.models import AccessToken
from oauth2_provider.models import Application
from oauthlib.common import generate_token

from users.messages import AccountActivationEmail


def send_activation_mail(user):
    '''
        Sends an activation email to the user
        param user: User instance
    '''
    AccountActivationEmail(user.email, user).send()


def create_token(user, app):
    '''
    Creates an AccessToken object for the user
    :param user: User instance
    :param type: class
    :param app: App instance
    :param type: class
    '''
    expire_second = settings.OAUTH2_PROVIDER['ACCESS_TOKEN_EXPIRE_SECONDS']
    expires = timezone.now() + timezone.timedelta(seconds=expire_second)
    access_token = AccessToken.objects.create(
        user=user,
        application=app,
        expires=expires,
        token=generate_token()
    )
    return access_token


def create_application(user):
    '''
    Creates an AccessToken object for the user
    :param user: User instance
    :param type: class
    '''

    name = f'myapp_{user.email}'
    app = Application.objects.create(
        user=user,
        name=name,
        authorization_grant_type='password',
        client_type='public',
    )
    return app
