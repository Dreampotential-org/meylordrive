from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db import models

import hashlib


class MonitorFeedback(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, default="")
    message = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True)


class GpsCheckin(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE,
                             default="")
    msg = models.CharField(max_length=2000, default='')
    lat = models.CharField(max_length=500, default='')
    lng = models.CharField(max_length=500, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    monitor_feedback = models.ManyToManyField(MonitorFeedback)


class VideoUpload(models.Model):
    videoUrl = models.CharField(max_length=500)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=500, default="")
    monitor_feedback = models.ManyToManyField(MonitorFeedback)

    def __str__(self):
        return self.videoUrl

    def video_source_link(self):
        url = self.videoUrl.split('/')
        video_id = url[-1]
        user_id = url[2]
        return '/review-video.html?id=%s&user=%s' % (video_id, user_id)

    def video_id(self):
        url = self.videoUrl.split('/')
        return url[-1]

    def video_api_link(self):
        url = self.videoUrl.split('/')
        video_id = url[-1]
        user_id = url[2]
        return '/api/review-video?id=%s&user=%s' % (video_id, user_id)

    def video_ref_link(self):
        url = self.videoUrl.split('/')
        video_id = url[-1]
        user_id = url[2]
        return '/review-video.html?id=%s&user=%s' % (video_id, user_id)

    def video_link(self):
        domain_name = Site.objects.last().domain
        url = self.videoUrl.split('/')
        video_id = url[-1]
        user_id = url[2]
        return '%s/video/?id=%s&user=%s' % (domain_name, video_id, user_id)

    def video_monitor_link(self):
        domain_name = Site.objects.last().domain
        url = self.videoUrl.split('/')
        url = self.videoUrl.split('/')
        video_id = url[-1]
        user_id = url[2]

        return '%s/video-monitor/?id=%s&user=%s' % (
            domain_name, video_id, user_id
        )


class SubscriptionEvent(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    subscription_id = models.TextField(default="")
    paying = models.BooleanField(default=False)


class Organization(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True)
    logo = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    hostname = models.CharField(max_length=500, default="")
    address = models.CharField(max_length=500, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    phone_no = models.CharField(max_length=100, blank=True, null=True)
    notify_all = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return self.name


class UserMonitor(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, default="")
    notify_email = models.EmailField(max_length=512, blank=True, null=True)


class OrganizationMember(models.Model):
    # should add unique to user not unique together
    user = models.ForeignKey(to=User, on_delete=models.CASCADE,
                             default="")
    admin = models.BooleanField(default=False, db_index=True)
    organization = models.ForeignKey(to=Organization, on_delete=models.CASCADE,
                                     null=True, blank=True)

    class Meta:
        unique_together = (("user"),)


class OrganizationMemberMonitor(models.Model):
    # if you want default to be null specify null = True in user and client
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, default="")
    client = models.ForeignKey(to=User,
                               on_delete=models.CASCADE, default="",
                               related_name='%(class)s_requests_created')


class UserProfileInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=17, blank=True, null=True)
    name = models.CharField(max_length=17, blank=True, null=True)
    phone_num = models.CharField(max_length=17, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    notify_email = models.EmailField(max_length=512, blank=True, null=True)
    days_sober = models.PositiveIntegerField(default=0, null=True)
    sober_date = models.CharField(max_length=256, blank=True, null=True)
    user_hash = models.CharField(max_length=256, blank=True, null=True)
    source = models.CharField(max_length=500, default="", null=True)
    stripe_subscription_id = models.CharField(max_length=256,
                                              blank=True, null=True)
    paying = models.BooleanField(default=False)
    iap_blurb = models.TextField(default="")
    user_org = models.ForeignKey(to=Organization,
                                 on_delete=models.SET_NULL,
                                 blank=True, null=True)

    login_code = models.CharField(max_length=17, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        if not self.id:
            self.user_hash = hashlib.sha1(
                self.user.email.encode('utf-8')
            ).hexdigest()
        super(UserProfileInfo, self).save(*args, **kwargs)


class UserLead(models.Model):
    phone = models.CharField(max_length=17, blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    website = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
