from django.shortcuts import render
from django.views.generic import (
    ListView,
    DeleteView,
    DetailView,
    CreateView, 
    UpdateView
)
from .models import Product

# Create your views here.
class ProductListView(ListView):
    template_name = "products/list.html"
    model = Product
    context_object_name = 'products'