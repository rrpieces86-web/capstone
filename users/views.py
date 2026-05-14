from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import SignupForm, ProfileForm

# Create your views here.

class UserLogin(LoginView):
    template_name = 'users/login.html'

class UserSignup(CreateView):
    model = User
    form_class = SignupForm
    template_name = 'users/signup.html'
    success_url = reverse_lazy('Login')

    def form_valid(self, form):
        user = form.save(commit=False)
        pass_text = form.cleaned_data['password']
        user.set_password(pass_text)
        user.save()
        return super().form_valid(form)
    

@login_required
def profile_view(request):
    return render(request, 'users/profile.html', {"profile": request.user.profile})
    
@login_required
def profile_edit_view(request):
    user = request.user
    profile = user.profile

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile, user=user)
        if form.is_valid():
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.email = form.cleaned_data["email"]
            user.save()
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("profile")
    else:
        form = ProfileForm(instance=profile, user=user)

    return render(request, "users/profile_edit.html", {"form": form})

