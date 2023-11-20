# views.py
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Room, Message
import json

@login_required
def rooms(request):
    rooms = Room.objects.all()
    return render(request, "rooms.html", {'rooms': rooms})

@login_required
def room(request, slug):
    room_name = slug
    api_key = 'your_api_key_here'  # Replace with the actual API key

    return render(
        request,
        "room.html",
        {
            'room_name': room_name,
            'api_key': api_key,
        }
    )

@csrf_exempt
def websocket_connect(request, room_name):
    """
    WebSocket connect view for the chat.
    """
    # You can customize the template name and context based on your needs
    template_name = 'websocket/connect.html'
    context = {'room_name': room_name}

    return render(request, template_name, context)

@csrf_exempt
def websocket_disconnect(request, room_name):
    """
    WebSocket disconnect view for the chat.
    """
    # You can customize the template name and context based on your needs
    template_name = 'websocket/disconnect.html'
    context = {'room_name': room_name}

    return render(request, template_name, context)

@csrf_exempt
def websocket_receive(request, room_name):
    """
    WebSocket receive view for the chat.
    """
    # You can customize the template name and context based on your needs
    template_name = 'websocket/receive.html'
    context = {'room_name': room_name}

    return render(request, template_name, context)

@csrf_exempt
def websocket_send(request, room_name):
    """
    WebSocket send view for the chat.
    """
    if request.method == 'POST':
        message = request.POST.get('message', '')
        username = request.user.username
        channel_layer = get_channel_layer()

        # Send the message to the room's group
        async_to_sync(channel_layer.group_send)(
            room_name,
            {
                'type': 'chat.message',
                'message': message,
                'username': username,
            }
        )

        return HttpResponse('Message sent.')
    else:
        return HttpResponse('Invalid request method.')

