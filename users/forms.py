from django import forms
from django.contrib.auth.models import User
from .models import Profile
 
 
class SignupForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "username", "password"]
 
 
class ProfileForm(forms.ModelForm):
    # Editable User fields
    first_name = forms.CharField(
        max_length=150, required=False,
        widget=forms.TextInput(attrs={"placeholder": "First name"})
    )
    last_name = forms.CharField(
        max_length=150, required=False,
        widget=forms.TextInput(attrs={"placeholder": "Last name"})
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={"placeholder": "you@example.com"})
    )
 
    class Meta:
        model = Profile
        fields = ["avatar", "bio", "phone", "address"]
        widgets = {
            "bio": forms.Textarea(attrs={
                "placeholder": "Tell us a bit about yourself…",
                "rows": 4,
            }),
            "phone": forms.TextInput(attrs={"placeholder": "+1 555 000 0000"}),
            "address": forms.TextInput(attrs={"placeholder": "City, State"}),
        }
 
    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields["first_name"].initial = user.first_name
            self.fields["last_name"].initial = user.last_name
            self.fields["email"].initial = user.email