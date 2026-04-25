from django.shortcuts import render

# Create your views here.
def home_view(request):
    return render(request, "public/home.html")
def about_view(request):
    return render(request, "public/about_us.html")