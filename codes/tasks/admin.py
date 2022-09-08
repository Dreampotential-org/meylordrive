from django.contrib import admin
from tasks.models import Task
from tasks.models import TaskLog
from tasks.models import TaskServer
from tasks.models import SystemSpecs
from tasks.models import Server
from tasks.models import KeyPair, ServerUserKey


class TaskAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "repo",)


class TaskLogAdmin(admin.ModelAdmin):
    pass


class TaskServerAdmin(admin.ModelAdmin):
    pass


class SystemSpecsAdmin(admin.ModelAdmin):
    pass


class ServerAdmin(admin.ModelAdmin):
    list_display = ("name", "ip_address", "alive",)


class KeyPairAdmin(admin.ModelAdmin):
    pass


class ServerUserKeyAdmin(admin.ModelAdmin):
    pass


admin.site.register(TaskServer, TaskServerAdmin)
admin.site.register(Server, ServerAdmin)
admin.site.register(SystemSpecs, SystemSpecsAdmin)
admin.site.register(TaskLog, TaskLogAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(KeyPair, KeyPairAdmin)
admin.site.register(ServerUserKey, ServerUserKeyAdmin)
