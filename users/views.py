from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, EmailAuthenticationForm, ProfileForm, UserRegistrationWithProfileForm

def login_view(request):
    if request.method == "POST":
        form = EmailAuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Check if profile is incomplete
            profile = getattr(user, 'profile', None)
            if not profile or not profile.full_name or not profile.date_of_birth or not profile.gender or not profile.weight_kg or not profile.height_cm:
                return redirect('users:create_profile')

            next_url = request.GET.get("next")
            if next_url:
                return redirect(next_url)

            return redirect("my_app:home")

    else:
        form = EmailAuthenticationForm()

    return render(request, "users/login.html", {"form": form})

def register(request):
    if request.method == "POST":
        form = UserRegistrationWithProfileForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Your account has been created and profile saved! You are now logged in.")
            return redirect('my_app:home')
    else:
        form = UserRegistrationWithProfileForm()
    return render(request, 'users/register.html', {'form': form})

@login_required(login_url='users:login')
def user(request):
    return render(request, "my_app/home.html")

@login_required(login_url='users:login')
def create_profile(request):
    # existing profile can be edited, but this view will be used to create/update initial details
    profile = getattr(request.user, 'profile', None)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.instance.user = request.user
            form.save()
            messages.success(request, 'Profile saved successfully.')
            return redirect('users:profile')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'users/create_profile.html', {'form': form})

@login_required(login_url='users:login')
def profile(request):
    return render(request, 'users/profile.html', {'profile': request.user.profile, 'user': request.user})

def logout_view(request):
    logout(request)
    messages.success(request, "Successfully logged out.")
    return redirect('users:login')