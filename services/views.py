from django.shortcuts import render, redirect
from django.views.generic import (
    ListView,
    DeleteView,
    DetailView,
    CreateView,
    UpdateView
)
from .models import Service
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY
# Create your views here.

class ServiceListView(ListView):
    template_name = 'services/list.html'
    model = Service
    context_object_name = 'services'

class ServiceDetailView(DetailView):
    template_name = 'services/detail.html'
    model = Service
    context_object_name = 'single_service'

class ServiceCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    template_name = 'services/new.html'
    model = Service
    fields = ["img", "title", "description", "price", "quantity"]

    def test_func(self):
        return self.request.user.is_staff
    
class ServiceUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = 'services/edit.html'
    model = Service
    fields = ["img", "title", "description", "price", "quantity"]

    def test_func(self):
        return self.request.user.is_staff
    

class ServiceDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    template_name = 'services/delete.html'
    model = Service
    success_url = reverse_lazy('service_list')
    context_object_name = 'item'

    def test_func(self):
        return self.request.user.is_staff
    

