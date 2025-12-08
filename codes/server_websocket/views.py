from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from .models import Room, Message
import uuid

def rooms(request):
    rooms = Room.objects.all()
    return render(request, "rooms.html", {"rooms": rooms})

def room(request, slug):
    # Get or create room
    room, created = Room.objects.get_or_create(
        slug=slug,
        defaults={'name': slug}
    )
    room_name = room.name
    messages = Message.objects.filter(room=room)

    return render(request, "room.html",
                  {"room_name": room_name, "slug": slug,
                   'messages': messages})

@login_required
def create_room(request):
    if request.method == 'POST':
        room_name = request.POST.get('room_name', '').strip()
        if room_name:
            # Create unique slug
            base_slug = slugify(room_name)
            slug = base_slug
            counter = 1
            while Room.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            # Create the room
            Room.objects.create(name=room_name, slug=slug)
            return redirect('rooms')
    
    return redirect('rooms')
