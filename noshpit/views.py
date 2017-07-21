from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.db import IntegrityError
from django.core import serializers
from django.db.models import Count

from .models import Photo, Location, Pit, PitPhoto, User, Vote
from pprint import pprint
from .forms import PitForm, JoinForm
import requests, logging, random, string
import json

def home(request):
    request.session.flush()
    return render(request, 'noshpit/home.html', {})

def start_a_pit(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = PitForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # find all the photos that conform to the form requirements
            photos = __find_photos__(form)
            # associate the photos with a pit ID and save them
            pit = Pit.objects.get(id=request.session["pit_id"])
            for photo in photos:
                pit_photo = PitPhoto(photo=photo, pit=pit)
                pit_photo.save()

            # need to create a new template start_noshing, and new view
            return redirect('start_noshing')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = PitForm()
        # print(request.session["pit_id"])
        # doesn't create a new pit on reload
        if "pit_id" not in request.session:
            token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            pit = Pit(token=token)
            pit.save()
            request.session["pit_id"] = pit.id

        # creates user and associates them with a pit
        if "user_id" not in request.session:
            pit = Pit.objects.get(id=request.session["pit_id"])
            user = User(pit=pit)
            user.save()
            request.session["user_id"] = user.id

    return render(request, 'noshpit/start_a_pit.html', {'form': form, 'token': token})

def join_a_pit(request):

    if request.method == 'POST':
        form = JoinForm(request.POST)

        if form.is_valid():
            pit = Pit.objects.get(token=form.cleaned_data["token"])
            request.session["pit_id"] = pit.id

            # create user
            if "user_id" not in request.session:
                user = User(pit=pit)
                user.save()
                request.session["user_id"] = user.id

            return redirect('start_noshing')

    else:
        form = JoinForm()

    return render(request, 'noshpit/join_a_pit.html', {'form': form})

def start_noshing(request):
    pit = Pit.objects.get(id=request.session["pit_id"])
    pit_token = pit.token
    return render(request, 'noshpit/start_noshing.html', {'pit_token':pit_token})

def list_photos(request):
    # finds photos assigned to a specific pit and randomizes their order

    if "photo_index" not in request.session:
        index = 0
        pit = Pit.objects.get(id=request.session["pit_id"])
        pit_photos = PitPhoto.objects.filter(pit=pit).order_by('?')
        pit_photos = [pit_photo.id for pit_photo in pit_photos]
        # print(pit_photos)
        request.session["pit_photos"] = pit_photos
    else:
        index = request.session["photo_index"] + 1
        pit_photos = request.session["pit_photos"]

    request.session["photo_index"] = index
    # print(pit_photos[index])
    pit_photo = PitPhoto.objects.get(id=pit_photos[index])

    # once we hit the last index redirect to another template

    return render(request, 'noshpit/list_photos.html', {'pit_photo': pit_photo})

def yes(request):
    # create a vote
    pit_photo = PitPhoto.objects.get(id=request.session["pit_photos"][request.session["photo_index"]])
    location = pit_photo.photo.location
    pit = Pit.objects.get(id=request.session["pit_id"])
    user = User.objects.get(id=request.session["user_id"])
    vote = Vote(location=location, user=user, pit=pit)

    try:
        vote.save()
    except IntegrityError:
        logging.info("This user already voted for this location")

    # check for winner
    # find num of users
    users = User.objects.filter(pit=request.session["pit_id"])
    num_users = len(users)
    # list of votes with users' count in them
    location_votes = Vote.objects.filter(pit=request.session["pit_id"]).values("location").annotate(Count('user'))
    # print(num_users)
    # print(users[0].id)
    # print(users[1].id)
    # print(location_votes)
    winner = location_votes.filter(user__count = num_users)

    if len(winner) > 0:
        # print("we have a winner!")
        # print(winners)
        pit.winner = location
        print(pit.winner)


    return redirect('photos')


def __find_photos__(form):

    url = 'https://maps.googleapis.com/maps/api/place'
    place_search = '/nearbysearch/json?key='
    details_search = '/details/json?key='
    photo_search = '/photo?key='
    key = settings.PLACES_KEY
    radius = '&radius' + str(form.cleaned_data["distance"])
    location_type = '&location=47.608090, -122.335000&radius=500&type=restaurant'

    response = requests.get(url + place_search + key + radius + location_type)
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
    return photos
