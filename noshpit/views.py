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
    # response.status not equal 200 do something
    restaurants = json.loads(response.text)
    # might need to make additional queries "next_page_token"
    photos = []

    for restaurant in restaurants["results"]:
        location = Location(place_id=restaurant["place_id"], name=restaurant["name"])
        try:
            location.save()
        except IntegrityError:
            logging.info("This location already exists")
            location = Location.objects.get(place_id=restaurant["place_id"])
            location_photos = Photo.objects.filter(location=location)
            # gets photos from the database
            photos += location_photos
            # if location already exists, no need to make extra api calls
            continue

        placeid = '&placeid=' + restaurant["place_id"]
        response = requests.get(url + details_search + key + placeid)
        details = json.loads(response.text)

        for detail in details["result"]["photos"]:
            max_height = '&maxheight=600'
            photoreference = '&photoreference=' + detail["photo_reference"]

            response = requests.get(url + photo_search + key + max_height + photoreference, allow_redirects=False)
            photo_url = response.headers["Location"]

            #  creates a photo object
            photo = Photo(location=location, url=photo_url)

            try:
                photo.save()
            except IntegrityError:
                logging.info("This photo url already exists")
                photo = Photo.objects.get(url=photo_url)

            photos.append(photo)

    # randomize order of photos
    # find a spot to save the randomized list of photos
    # push that out to the user one at a time
    # (another view that would return one photo and pop it and call it on every click of a button)
    return render(request, 'noshpit/list_photos.html', {'photos':photos})
