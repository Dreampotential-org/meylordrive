from django.contrib import admin
from tasks.models import GithubHook


class GitHubAdmin(admin.ModelAdmin):
    pass


admin.site.register(GithubHook, GitHubAdmin)
