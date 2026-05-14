from django.urls import path
from django.contrib.auth.views import (
    LogoutView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,

)
from . import views

urlpatterns = [
    path('login/', views.UserLogin.as_view(), name="Login"),
    path('signup/', views.UserSignup.as_view(), name="Signup"),
    path('logout/', LogoutView.as_view(), name='logout'),

    path(
        "password-reset/",
        PasswordResetView.as_view(
            template_name="users/password_reset.html",
            email_template_name="users/password_reset_email.txt",
            subject_template_name="users/password_reset_subjecct.txt",
            success_url="/users/password-reset/done/",
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        PasswordResetDoneView.as_view(template_name="users/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "password-reset/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html",
            success_url="/users/password-reset/complete/",
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        PasswordResetCompleteView.as_view(
            template_name="users/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),

    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name="profile_edit"),
]