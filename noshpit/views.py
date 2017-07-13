from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.db import IntegrityError
from .models import Photo, Location
import requests, logging
import json
from pprint import pprint

def home(request):
    return render(request, 'noshpit/home.html', {})

def start_a_pit(request):
    return render(request, 'noshpit/start_a_pit.html', {})

def join_a_pit(request):
    return render(request, 'noshpit/join_a_pit.html', {})

def list_photos(request):
    url = 'https://maps.googleapis.com/maps/api/place'
    place_search = '/nearbysearch/json?key='
    details_search = '/details/json?key='
    photo_search = '/photo?key='
    key = settings.PLACES_KEY
    location_type = '&location=47.608090, -122.335000&radius=500&type=restaurant'

    response = requests.get(url + place_search + key + location_type)
    restaurants = json.loads(response.text)
    # might need to make additional queries "next_page_token"

    for restaurant in restaurants["results"]:
        location = Location(place_id=restaurant["place_id"], name=restaurant["name"])
        try:
            location.save()
        except IntegrityError:
            logging.info("This location already exists")

        placeid = '&placeid=' + restaurant["place_id"]
        response = requests.get(url + details_search + key + placeid)
        details = json.loads(response.text)

        # print(response.url)
        for detail in details["result"]["photos"]:
            max_height = '&maxheight=600'
            photoreference = '&photoreference=' + detail["photo_reference"]
            response = requests.get(url + photo_search + key + max_height + photoreference, allow_redirects=False)
            # print(response.headers["Location"])
            photo = Photo(location=Location.objects.get(place_id=restaurant["place_id"]), url=response.headers["Location"])

            try:
                photo.save()
            except:
                looging.info("Soething went wrong and it didn't save")

        # request photos


    # r = requests.get('https://maps.googleapis.com/...', allow_redirects=False)
    # r.headers["Location"]


    # photos = Photo.objects.all()
    # return render(request, 'noshpit/list_photos.html', {'photos':photos})
    restaurant_names = Location.objects.all()
    return render(request, 'noshpit/list_photos.html', {'restaurant_names': restaurant_names})
