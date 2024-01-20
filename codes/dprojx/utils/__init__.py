from django.http import HttpResponse
from django.shortcuts import render

from xppda.models import UserProfileInfo


def superuser_only(function):
    def _inner(request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponse(
                'Admin access required <a href="/admin">Admin Login</a>')
        return function(request, *args, **kwargs)
    return _inner


def custom_render(request, template, values={}):
    if request.user.is_authenticated:
        profile = UserProfileInfo.objects.filter(
            user__email=request.user.email
        ).first()
        if profile:
            values['notify_email'] = profile.notify_email

    return render(request, template, values)
