from django.db import models

class SogAub(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.TextField()

class Sog(models.Model):
    name = models.TextField()
    seconds = models.IntegerField(default=0)
    sog_group = models.ForeignKey(
        SogAub, on_delete=models.CASCADE,
        null=True, blank=True, default=None
    )


