# tasks/models.py
from django.db import models
from django.contrib.auth.models import User

class Room(models.Model):
    name = models.CharField(max_length=20)
    slug = models.SlugField(max_length=100)

    def __str__(self):
        return f"Room: {self.name} | Id: {self.slug}"

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message is: {self.content}"

class StatsEntry(models.Model):
    system = models.CharField(max_length=255)
    node_name = models.CharField(max_length=255)
    release = models.CharField(max_length=255)
    version = models.CharField(max_length=255)
    machine = models.CharField(max_length=255)
    processor = models.CharField(max_length=255)
    ip_address = models.CharField(max_length=255)
    mac_address = models.CharField(max_length=255)
    total_swap = models.CharField(max_length=255)
    swap_free = models.CharField(max_length=255)
    used_swap = models.CharField(max_length=255)
    swap_percentage = models.FloatField()
    total_bytes_sent = models.CharField(max_length=255)
    total_bytes_received = models.CharField(max_length=255)

    def __str__(self):
        return f"Stats Entry for System: {self.system}"

class ApiKey(models.Model):
    key = models.CharField(max_length=255)

    def __str__(self):
        return f"API Key: {self.key}"

class Agent(models.Model):
    api_key = models.ForeignKey(ApiKey, on_delete=models.CASCADE)
    alive = models.BooleanField(default=False)

    def __str__(self):
        return f"Agent with API Key: {self.api_key.key}"
