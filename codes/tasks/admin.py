from django.contrib import admin
from tasks.models import GithubHook
from tasks.models import Task
from tasks.models import Pipeline
from tasks.models import TaskLog
from tasks.models import PipelineServer
from tasks.models import SystemSpecs
from tasks.models import Server


class GitHubAdmin(admin.ModelAdmin):
    list_display = [field.name for field in GithubHook._meta.get_fields()]


class TaskAdmin(admin.ModelAdmin):
    pass
    #list_display = [field.name for field in Task._meta.get_fields()]


class PipelineAdmin(admin.ModelAdmin):
    #list_display = [field.name for field in Pipeline._meta.get_fields()]
    pass


class TaskLogAdmin(admin.ModelAdmin):
    list_display = [field.name for field in TaskLog._meta.get_fields()]


class PipelineServerAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PipelineServer._meta.get_fields()]


class SystemSpecsAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in SystemSpecs._meta.get_fields()]
    pass


class ServerAdmin(admin.ModelAdmin):
    #list_display = [field.name for field in Server._meta.get_fields()]
    pass


admin.site.register(PipelineServer, PipelineServerAdmin)
admin.site.register(Server, ServerAdmin)
admin.site.register(SystemSpecs, SystemSpecsAdmin)
admin.site.register(TaskLog, TaskLogAdmin)
admin.site.register(Pipeline, PipelineAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(GithubHook, GitHubAdmin)
