import resend
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .forms import ContactForm
 
 
def home_view(request):
    return render(request, "public/home.html")
 
 
def about_view(request):
    return render(request, "public/about_us.html")
 
 
@login_required
def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            message = form.cleaned_data['message']
 
            resend.api_key = settings.RESEND_API_KEY
 
            resend.Emails.send({
                "from": "onboarding@resend.dev",
                "to": "rrpieces86@gmail.com",
                "reply_to": email,
                "subject": f"Contact Form Submission from {name}",
                "text": f"Name: {name}\nEmail: {email}\nPhone: {phone}\n\nMessage:\n{message}",
            })
 
            messages.success(request, 'Your message was sent successfully!')
            return redirect('contact')
    else:
        form = ContactForm()
 
    return render(request, 'public/contact.html', {'form': form})