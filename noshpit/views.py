from django.shortcuts import render, get_object_or_404
from django.conf import settings
from .models import Photo, Location
import requests
import json
from pprint import pprint

def home(request):
    return render(request, 'noshpit/home.html', {})

def start_a_pit(request):
    return render(request, 'noshpit/start_a_pit.html', {})

def join_a_pit(request):
    return render(request, 'noshpit/join_a_pit.html', {})

def list_photos(request):

    key = settings.PLACES_KEY
    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?key=' + key + '&location=47.608090, -122.335000&radius=500&type=restaurant'

    response = requests.get(url)
    restaurants = json.loads(response.text)
    # might need to make additional queries "next_page_token"

    for restaurant in restaurants["results"]:
        # if place_id already exists in the database
            # do nothing
        # else
        location = Location(place_id=restaurant["place_id"], name=restaurant["name"])
        location.save()

        # request photos


    # r = requests.get('https://maps.googleapis.com/...', allow_redirects=False)
    # r.headers["Location"]


    # photos = Photo.objects.all()
    # return render(request, 'noshpit/list_photos.html', {'photos':photos})
    restaurant_names = Location.objects.all()
    return render(request, 'noshpit/list_photos.html', {'restaurant_names': restaurant_names})
