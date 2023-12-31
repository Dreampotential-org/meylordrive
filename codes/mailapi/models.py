from django.db import models
from django.contrib.auth import get_user_model
import hashlib


class Site(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,
                             null=True, blank=True, default=None)
    name = models.TextField(blank=True, null=True)


class Account(models.Model):
    email = models.CharField(max_length=512, unique=True)
    password = models.CharField(max_length=512)
    active_on_server = models.BooleanField(default=False)
    hash_password = models.CharField(max_length=512, blank=True, null=True)

    def __str__(self):
        return self.email


class Mail(models.Model):
    message_id = models.CharField(max_length=512, blank=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    mail_from = models.EmailField()
    mail_to = models.EmailField()
    subject = models.CharField(max_length=512)
    message = models.TextField()
    body = models.TextField(blank=True, null=True)
    local_date = models.CharField(max_length=128)
    row_date = models.CharField(max_length=128)
    read = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    draft = models.BooleanField(default=False)

    def gen_message_id(self):
        val = self.account.email + self.subject + '-' + self.row_date
        return hashlib.sha256(val.encode()).hexdigest()

    def save(self, *args, **kwargs):
        self.message_id = self.gen_message_id()
        super(Mail, self).save(*args, **kwargs)
