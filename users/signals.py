from django.db.models.signals import post_save, post_delete, post_init
from django.dispatch import receiver
from django.core.mail import send_mail
from django.urls import reverse
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created

from config import settings
from users.models import UserAccount


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    site = 'http://127.0.0.1:8000'

    email_plaintext_message = "{}?token={}".format(reverse('password_reset:reset-password-confirm'), reset_password_token.key)
    reset_url = site + email_plaintext_message

    send_mail(
        "Password Reset for {title}".format(title="Some website title"),
        reset_url,
        "noreply@somehost.local",
        [reset_password_token.user.email]
    )
