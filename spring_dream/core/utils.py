from django.conf import settings
from django.contrib.auth.models import User
from django.core import mail
from django.urls import reverse
from django.utils import timezone

from oauthlib.common import generate_token
from oauth2_provider.models import AccessToken, Application

def send_activation_mail(user):
    '''
        Sends an activation email to the user
        param user: User instance
        param token: AccessToken instance
    '''


    from_email = 'Account Activation <{settings.EMAIL_HOST_USER}>'
    auth_token = AccessToken.objects.get(user=user)
    activation_url = reverse('api:users-v1:user-detail', kwargs={'pk': user.id})
    body = f'''
        Hi, thank you for signing up on our app.
        Here is your auth token activate your account {auth_token}.
        Activate your account here: {settings.SITE_URL}{activation_url}
        Thanks. 
        The App Team.
    '''

    # The user's hash will be used as a token
    html_body = f'<div>{body}</div>'
    email = mail.EmailMultiAlternatives(
        'Account Activation',
        body,
        from_email,
        [user.email],
    )
    email.attach_alternative(html_body, "text/html")
    email.send()


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