from django.shortcuts import render
from django.views.generic import (
    ListView,
    DeleteView,
    DetailView,
    CreateView, 
    UpdateView
)
from .models import Product
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


# Create your views here.
class ProductListView(ListView):
    template_name = "products/list.html"
    model = Product
    context_object_name = 'products'

class ProductDetailView(DetailView):
    template_name = 'products/detail.html'
    model = Product
    context_object_name = 'single_product'

class ProductCreateView(LoginRequiredMixin,UserPassesTestMixin,CreateView):
    template_name = 'products/new.html'
    model = Product
    fields = ["img", "title", "brand", "category", "description", "price", "quantity"]

    def test_func(self):
        return self.request.user.is_staff
    

class ProductUpdateView(LoginRequiredMixin,UserPassesTestMixin,UpdateView):
    template_name = 'products/edit.html'
    model = Product
    fields = ["img", "title", "brand", "category", "description", "price", "quantity"]

    def test_func(self):
        return self.request.user.is_staff

class ProductDeleteView(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    template_name = 'products/delete.html'
    model = Product
    success_url = reverse_lazy('product_list')
    context_object_name = 'item'

    def test_func(self):
        return self.request.user.is_staff
