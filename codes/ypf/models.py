from django.db import models
from django.contrib.auth import get_user_model



class Artic(models.Model):
    title = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True)
    message = models.TextField(default="")
    user = models.ForeignKey(to=get_user_model(),
                             on_delete=models.CASCADE,
                             blank=True, null=True)

