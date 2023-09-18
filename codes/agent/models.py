from django.db import models

from django.contrib.auth import get_user_model

class ApiKey(models.Model):
    key = models.CharField(max_length=255)
    user = models.ForeignKey(get_user_model(),
                             on_delete=models.CASCADE,
                             null=True, blank=True,
                             default=None)
class Agent(models.Model):
    ip_address = models.CharField(max_length=100)
    api_key = models.ForeignKey(
        ApiKey, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(),
                             on_delete=models.CASCADE,
                             null=True, blank=True,
                             default=None)


