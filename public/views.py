from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import ContactForm

# Create your views here.
def home_view(request):
    return render(request, "public/home.html")
def about_view(request):
    return render(request, "public/about_us.html")

@login_required
def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        print("Form valid:", form.is_valid())  # add this
        print("Form errors:", form.errors)     # add this
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            message = form.cleaned_data['message']

            send_mail(
                subject=f'Cantact Form Submission from {name}',
                message=f'Name: {name}\nEmail: {email}\nPhone: {phone}\n\nMessage:\n{message}',
                from_email=email,
                recipient_list=['rrpieces86@gmail.com'],
                fail_silently=False,
            )
            messages.success(request, 'Your message was sent successfully!')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'public/contact.html', {'form': form})