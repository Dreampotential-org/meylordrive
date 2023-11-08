from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required

def login(request):
    if request.method == 'GET':
        # Add your login logic here
        # If the login is successful, redirect to the desired URL
        return HttpResponseRedirect("https://voice.google.com/u/0/calls")
    return render(request, 'login.html')

@login_required
def home(request):
    return render(request, 'home.html')

@login_required
def logout_view(request):
    auth_logout(request)
    return redirect('login')

def signup(request):
    if request.method == 'POST':
        # Add your signup logic here
        return redirect('login')
    return render(request, 'signup.html')
