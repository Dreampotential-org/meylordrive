from django.db import models


class Sog(models.Model):
    name = models.TextField()
    seconds = models.IntegerField(default=0)
    sog_group = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE,
        null=True, blank=True, default=None
    )


class SogAub(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,
                             null=True, blank=True, default=None)

