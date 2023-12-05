from django.db import models
import hashlib


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
    local_date = models.CharField(max_length=128)
    row_date = models.CharField(max_length=128)

    def gen_message_id(self):
        val = self.account.email + self.subject + '-' + self.row_date
        return hashlib.sha256(val.encode()).hexdigest()

    def save(self, *args, **kwargs):
        self.message_id = self.gen_message_id()
        super(Mail, self).save(*args, **kwargs)
