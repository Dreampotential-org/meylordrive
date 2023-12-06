from django.db import models

class GoogleCo(models.Model):
    keywords = models.TextField()
    created_at = models.DateTimeField(auto_now=True)

class GoogleTarget(models.Model):
    name = models.TextField()
    created_at = models.DateTimeField(auto_now=True)


class GoogleClick(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    search_term = models.TextField()
    url = models.TextField()
    co = models.ForeignKey(GoogleCo, on_delete=models.CASCADE)
    target = models.ForeignKey(GoogleTarget, on_delete=models.CASCADE)
