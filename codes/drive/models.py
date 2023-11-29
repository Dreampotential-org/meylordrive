from django.db import models

# Create your models here.
class Phone(models.Model):
    number = models.CharField(max_length=20, unique=True)


class SMS(models.Model):
    number = models.CharField(max_length=20, blank=True, null=True)
    msg = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)
    source_phone = models.ForeignKey(
        to=Phone, on_delete=models.CASCADE,
        default=None
    )


class Contact(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=100, blank=True, null=True)
    owner_phone_other = models.CharField(
        max_length=100, blank=True, null=True)
    url = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    price = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    home_type = models.TextField(blank=True, null=True)

class Call(models.Model):
    contact = models.ForeignKey(to=Contact, on_delete=models.CASCADE,
                               default=None)
    phone_number = models.ForeignKey(
        to=Phone, on_delete=models.CASCADE,
        default="", related_name="call_phone_number")
    number = models.CharField(max_length=20,blank=True,null=True)
    created_at = models.DateTimeField(auto_now=True)
    time_duration = models.IntegerField(default=0)

    source_phone = models.ForeignKey(
        to=Phone, on_delete=models.CASCADE,
        default=None
    )



