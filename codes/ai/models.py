from django.db import models


class ChatApiRequest(models.Model):
    input_content = models.TextField()
    response_content = models.TextField()
    model = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    input_content = models.TextField()
    prompt_tokens = models.IntegerField(default=0)
    completion_tokens = models.IntegerField(default=0)
    total_tokens = models.IntegerField(default=0)
    asked_amount = models.IntegerField(default=0)
