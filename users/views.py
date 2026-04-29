from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from .forms import SignupForm

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