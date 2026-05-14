from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home_view, name='home'),
    path('', views.home_view, name='root'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact')
]