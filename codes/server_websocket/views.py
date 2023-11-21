from django.http import HttpResponseRedirect
from django.shortcuts import render,redirect
from django.urls import reverse
from .models import Room,Message
from django.middleware.csrf import get_token
from django.utils.text import slugify  # Import the slugify function

def rooms(request):
    rooms=Room.objects.all()
    return render(request, "rooms.html",{
     'rooms':rooms         }    )
def room(request, slug):
    context = {
        "slug": slug,
        "csrf_token": get_token(request),
    }

    return render(request, "room.html", context)
from .utils import generate_unique_slug  # Import the function

def create_room(request):
    if request.method == 'POST':
        room_name = request.POST.get('room_name')
        # Create room logic here, e.g., save to the database
        room = Room.objects.create(name=room_name, slug=generate_unique_slug(Room, room_name))
        # Redirect to the room view or wherever you want to go after creating the room
        return redirect('room', slug=room.slug)
    return render(request, 'create_room.html')