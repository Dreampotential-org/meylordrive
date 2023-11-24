from django.contrib import admin
from .models import Room, Message, WebSocketConnection

class MessageInline(admin.TabularInline):
    model = Message
    extra = 1

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    inlines = [MessageInline]

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'content', 'room', 'created_on')

@admin.register(WebSocketConnection)
class WebSocketConnectionAdmin(admin.ModelAdmin):
    list_display = ('room_group', 'connection_time', 'user')

# admin.site.register(WebSocketConnection, WebSocketConnectionAdmin)
