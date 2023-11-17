from django.db import models

# Create your models here.
class JsError(models.Model):
    message = models.TextField(blank=True, null=True)
    url = models.TextField(blank=True, null=True)
    lineNo = models.TextField(blank=True, null=True)
    columnNo  = models.TextField(blank=True, null=True)
    error_msg  = models.TextField(blank=True, null=True)

    # server address
    # client ip and other info..


