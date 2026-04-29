from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('login/', views.UserLogin.as_view(), name="Login"),
    path('signup/', views.UserSignup.as_view(), name="Signup"),
    path('logout/', LogoutView.as_view(), name='logout')
]