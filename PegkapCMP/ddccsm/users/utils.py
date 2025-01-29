from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.conf import settings

def send_password_reset_notification(user, reset_by=None, new_password=None):
    subject = _('Ο κωδικός σας άλλαξε - ΔΔCCSM')
    
    context = {
        'user': user,
        'reset_by': reset_by,
        'new_password': new_password,
        'site_name': 'ΔΔCCSM'
    }
    
    html_message = render_to_string('users/emails/password_reset_notification.html', context)
    plain_message = render_to_string('users/emails/password_reset_notification.txt', context)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message
    ) 