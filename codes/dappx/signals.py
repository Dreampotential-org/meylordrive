from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import UserLead
from .email_utils import send_email
# from .slack_helper import slack_send_msg


@receiver(post_save, sender=UserLead)
def userlead_created(sender, instance, created, **kwargs):
    if created:
        title = "New Lead"
        msg = f"you have a new lead with the following info \n" \
              f"email: {instance.email}\n"\
              f"name: {instance.name}\n"\
              f"phone: {instance.phone}\n"\
              f"website: {instance.website}\n"
        send_email("aaronorosen@gmail.com", title, msg)
        send_email("aaronorosen2@gmail.com", title, msg)
        # slack_send_msg(msg)