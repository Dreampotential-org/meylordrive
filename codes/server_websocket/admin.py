from django.contrib import admin
from .models import Room, Message, UserRoomActivity

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'content', 'room', 'created_on')
@admin.register(UserRoomActivity)
class UserRoomActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'entry_time', 'exit_time', 'duration')  # Include 'duration' in list_display
    date_hierarchy = 'entry_time'


# # rom .models import UserRoomActivity
# from django.utils import timezone
# from django.utils.translation import gettext_lazy as _

# from .models import UserRoomActivity
# class UserRoomActivityAdmin(admin.ModelAdmin):
#     list_display = ('user', 'room', 'entry_time', 'exit_time')

#     def get_form(self, request, obj=None, **kwargs):
#         form = super().get_form(request, obj, **kwargs)
#         form.base_fields['entry_time'].timezone = timezone.get_current_timezone()
#         form.base_fields['exit_time'].timezone = timezone.get_current_timezone()
#         return form

# admin.site.register(UserRoomActivity, UserRoomActivityAdmin)