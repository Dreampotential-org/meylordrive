from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Use Django's authentication system to check if the credentials are valid
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # User is authenticated, log them in
            auth_login(request, user)
            return HttpResponseRedirect("https://voice.google.com/u/0/calls")
        else:
            # Authentication failed, you might want to display an error message or redirect to the login page
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')


@login_required
def home(request):
        
        return HttpResponseRedirect("https://voice.google.com/u/0/calls")

@login_required
def logout_view(request):
    auth_logout(request)
    return redirect('login')

def signup(request):
    if request.method == 'POST':
        # Add your signup logic here
        return redirect('login')
    return render(request, 'signup.html')
