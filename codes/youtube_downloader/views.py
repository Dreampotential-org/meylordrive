# new_youtube/views.py
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from .models import YProfile, YouTubeProfile, YouTubeVideo  # Import YouTubeVideo model from the storage app
from django.contrib.auth.decorators import login_required

# @login_required
# from django_analytics import Analytic  # Import Django Analytics model

# @login_required
@login_required
def home(request):
    youtube_profiles = YouTubeProfile.objects.all()

    user_playlist = None
    try:
        # Retrieve the user profile using YProfile model
        user_profile = YProfile.objects.get(user=request.user)

        # Access the playlist through the user profile
        user_playlist = user_profile.playlist.all()
    except YProfile.DoesNotExist:
        pass  # Handle the exception if needed, or simply ignore

    return render(request, 'home.html', {'youtube_profiles': youtube_profiles, 'user_playlist': user_playlist})

@login_required
def add_to_playlist(request, profile_id):
    if request.method == 'POST':
        youtube_profile = get_object_or_404(YouTubeProfile, pk=profile_id)
        user = request.user

        # Print statements for debugging
        print(f"Adding profile to playlist: {youtube_profile.profile_name} for user: {user.username}")

        user_profile, created = YProfile.objects.get_or_create(user=user)
        user_profile.playlist.add(youtube_profile)

        # Print statements for debugging
        print(f"Playlist after addition: {user_profile.playlist.all()}")

        return redirect('home')
    # Handle GET request, render the home template
    youtube_profiles = YouTubeProfile.objects.all()
    return render(request, 'home.html', {'youtube_profiles': youtube_profiles, 'user_playlist': request.user.userprofile.playlist.all()})
# new_youtube/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
from .models import YouTubeVideo  # Import YouTubeVideo model from the storage app
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.core.files import File
from django.conf import settings
import os

@csrf_exempt
def get_media(request):
    videos = YouTubeVideo.objects.all()
    resp = []

    for video in videos:
        resp.append({
            'id': video.id,
            'title': video.title,
            'url': video.url,
            'description': video.description,
            'video_file': f'/download/{video.id}/',
        })

    return JsonResponse(resp, safe=False, json_dumps_params={'indent': 2})

def download_video(request, video_id):
    try:
        video = YouTubeVideo.objects.get(id=video_id)
        video_path = os.path.join(settings.MEDIA_ROOT, str(video.id) + ".mp4")

        # Check if the file exists
        if os.path.exists(video_path):
            with open(video_path, 'rb') as file:
                response = HttpResponse(file.read(), content_type='video/mp4')
                response['Content-Disposition'] = f'attachment; filename="{video.title}.mp4"'
                return response
        else:
            return HttpResponse("File not found", status=404)

    except YouTubeVideo.DoesNotExist:
        return HttpResponse("Video not found", status=404)
from django.http import JsonResponse

def playlist_detail(request, profile_id):
    youtube_profile = get_object_or_404(YouTubeProfile, pk=profile_id)
    videos = youtube_profile.videos.all()

    # Create a list to hold video data
    video_data = []

    for video in videos:
        video_data.append({
            'id': video.id,
            'title': video.title,
            'url': video.url,
            'description': video.description,
            'video_file': f'/download/{video.id}/',
        })

    # Return video data as JSON response
    return JsonResponse(video_data, safe=False, json_dumps_params={'indent': 2})