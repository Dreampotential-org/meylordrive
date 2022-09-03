from django.contrib import admin
from tasks.models import Task
from tasks.models import TaskLog
from tasks.models import TaskServer
from tasks.models import SystemSpecs
from tasks.models import Server


class TaskAdmin(admin.ModelAdmin):
    pass
    #list_display = [field.name for field in Task._meta.get_fields()]


class TaskLogAdmin(admin.ModelAdmin):
    list_display = [field.name for field in TaskLog._meta.get_fields()]


class TaskServerAdmin(admin.ModelAdmin):
    list_display = [field.name for field in TaskServer._meta.get_fields()]


class SystemSpecsAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in SystemSpecs._meta.get_fields()]
    pass


class ServerAdmin(admin.ModelAdmin):
    #list_display = [field.name for field in Server._meta.get_fields()]
    pass


admin.site.register(TaskServer, TaskServerAdmin)
admin.site.register(Server, ServerAdmin)
admin.site.register(SystemSpecs, SystemSpecsAdmin)
admin.site.register(TaskLog, TaskLogAdmin)
admin.site.register(Task, TaskAdmin)
