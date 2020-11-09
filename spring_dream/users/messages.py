from django.conf import settings
from django.urls import reverse

from oauth2_provider.models import AccessToken

from core.messages import EmailMessageBase

class AccountActivationEmail(EmailMessageBase):

    subject = 'Account Activation'
    txt_template = 'users/emails/account_activation.txt'
    html_template = 'users/emails/account_activation.html'
    from_email = 'Account Activation <{settings.EMAIL_HOST_USER}>'

    def __init__(self, recipients, user, *args, **kwargs):
        self.recipients = recipients
        self.user = user

    def get_context_data(self):
        context_data = {}
        # The user's password's hash will be used as a token
        algo, salt, p_hash = self.user.password.split('$', 2)
        context_data['auth_token'] = p_hash
        detail_url = reverse(
            'api:users-v1:user-activate', kwargs={'pk': self.user.id})
        context_data['activation_url'] = (
            f'{settings.SITE_URL}{detail_url}'
        )
        return context_data
