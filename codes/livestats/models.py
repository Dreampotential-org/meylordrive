from django.db import models
# from django.db import models

class WebSocketConnection(models.Model):
    room_group = models.CharField(max_length=255)
    connection_time = models.DateTimeField()

    def __str__(self):
        return f"Connection for {self.room_group} at {self.connection_time}"

class JsError(models.Model):
    message = models.TextField(blank=True, null=True)
    url = models.TextField(blank=True, null=True)
    lineNo = models.TextField(blank=True, null=True)
    columnNo  = models.TextField(blank=True, null=True)
    error_msg  = models.TextField(blank=True, null=True)
