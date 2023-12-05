from django.contrib import admin
from mailapi.models import Account, Mail


class MailAdmin(admin.ModelAdmin):
    list_display = ('account', 'subject', 'row_date',)


class AccountAdmin(admin.ModelAdmin):
    list_display = ('email', 'password', 'active_on_server',)


admin.site.register(Account, AccountAdmin)
admin.site.register(Mail, MailAdmin)
