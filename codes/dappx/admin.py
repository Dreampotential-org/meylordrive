from django.contrib import admin

from dappx.models import UserProfileInfo
from dappx.models import GpsCheckin
from dappx.models import User
from dappx.models import VideoUpload
from dappx.models import UserMonitor
from dappx.models import MonitorFeedback
from dappx.models import SubscriptionEvent
from dappx.models import Organization
from dappx.models import OrganizationMember
from dappx.models import OrganizationMemberMonitor
from .models import UserLead
from django.utils.html import format_html


class CustomVideoUpload(admin.ModelAdmin):
    list_display = ['id', 'user', 'display_link', 'created_at']

    def display_link(self, obj):
        user_hash = obj.videoUrl.split("/media/")[1].split("/")[0]
        video_id = obj.videoUrl[7:].split("/", 1)[1]
        url = '/video?id=%s&user=%s' % (video_id, user_hash)
        return format_html(
            '<video controls="" name="media" width="320" height="240">'
            '<source src="/video/?id=%s&amp;user=%s" type="video/mp4"></video>'
            % (video_id, user_hash)
        )

        return format_html(
            '<a href="%s" target="_blank">Play Video</a>' % (url)
        )

    display_link.mark_safe = True
    display_link.short_description = "URL"
    list_filter = ['user']
    model = VideoUpload


class CustomGpsCheckin(admin.ModelAdmin):
    list_display = ['id', 'msg', 'user', 'created_at']
    list_filter = ['user']
    model = GpsCheckin

    def user(self, obj):
        return obj.user.name

    def view_map(self, obj):
        print(obj.lat)
        print(obj.lng)

        map_url = 'https://www.google.com/maps/place/'
        map_url += "%s,%s" % (obj.lat, obj.lng)

        return format_html(
            '<a href="%s" target="_blank">View Map</a>' % map_url
        )


class UserProfileInfoAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'name', 'created_at', 'paying', 'iap_blurb',
    ]
    ordering = ('-id',)


class CustomUserMonitor(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'notify_email',
    ]
    ordering = ('-id',)


class CustomMonitorFeedback(admin.ModelAdmin):
    list_display = [
        'user', 'message',
    ]
    ordering = ('-id',)


class CustomSubscriptionEvent(admin.ModelAdmin):
    list_display = [
        'created_at', 'user', 'paying', 'subscription_id',
    ]
    ordering = ('-id',)


class CustomOrganization(admin.ModelAdmin):
    list_display = [
        'name', 'logo'
    ]
    ordering = ('-id',)


class CustomOrganizationMember(admin.ModelAdmin):
    list_display = [
        'user',
    ]
    ordering = ('-id',)
    #list_per_page = 10
    #list_max_show_all = 50


class CustomOrganizationMemberMonitor(admin.ModelAdmin):
    list_display = [
        'user', 'client'
    ]
    ordering = ('-id',)


class UserLeadAdmin(admin.ModelAdmin):
    list_display = ['email', 'name', 'phone', 'website', 'created_at']

# Register your models here.
admin.site.register(UserProfileInfo, UserProfileInfoAdmin)
admin.site.register(GpsCheckin, CustomGpsCheckin)
admin.site.register(VideoUpload, CustomVideoUpload)
admin.site.register(UserMonitor, CustomUserMonitor)
admin.site.register(MonitorFeedback, CustomMonitorFeedback)
admin.site.register(SubscriptionEvent, CustomSubscriptionEvent)
admin.site.register(Organization, CustomOrganization)
admin.site.register(OrganizationMember, CustomOrganizationMember)
admin.site.register(OrganizationMemberMonitor, CustomOrganizationMemberMonitor)
admin.site.register(UserLead, UserLeadAdmin)
