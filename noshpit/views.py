from django.shortcuts import render, get_object_or_404
from .models import Photo

def home(request):
    return render(request, 'noshpit/home.html', {})

def start_a_pit(request):
    return render(request, 'noshpit/start_a_pit.html', {})

def join_a_pit(request):
    return render(request, 'noshpit/join_a_pit.html', {})

def list_photos(request):
    photos = Photo.objects.all()
    return render(request, 'noshpit/list_photos.html', {'photos':photos})
