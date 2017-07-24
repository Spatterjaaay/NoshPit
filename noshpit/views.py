from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.conf import settings
from django.db import IntegrityError
from django.core import serializers
from django.db.models import Count

from .models import Photo, Location, Pit, PitPhoto, User, Vote
from pprint import pprint
from .forms import PitForm, JoinForm, EmailForm
import requests, logging, random, string
from .sendmail import sendmail
import json
from .restaurant import Restaurant

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
        inviteform = EmailForm()
        # doesn't create a new pit on reload
        if "pit_id" not in request.session:
            token = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for i in range(5))
            pit = Pit(token=token)
            pit.save()
            request.session["pit_id"] = pit.id
            request.session["token"] = token
        else:
            # in case user reloads, we still need to pass a token to the view
            token = request.session["token"]

        # creates user and associates them with a pit
        if "user_id" not in request.session:
            pit = Pit.objects.get(id=request.session["pit_id"])
            user = User(pit=pit)
            user.save()
            request.session["user_id"] = user.id

    return render(request, 'noshpit/start_a_pit.html', {'form': form, 'token': token, 'inviteform': inviteform})

def invite(request):
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            token = request.session["token"]
            sender = 'noreply@noshpit.net'
            destination = form.cleaned_data["email"]
            message = render_to_string('noshpit/invite.txt', {'sender': sender, 'destination': destination,'token': token})
            sendmail(sender, destination, message)

    return redirect('start')

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
    pit = Pit.objects.get(id=request.session["pit_id"])

    if pit.winner:
        return redirect('winner_detail')

    if "photo_index" not in request.session:
        index = 0
        # finds photos assigned to a specific pit and randomizes their order
        pit_photos = PitPhoto.objects.filter(pit=pit).order_by('?')
        pit_photos = [pit_photo.id for pit_photo in pit_photos]
        request.session["pit_photos"] = pit_photos
    else:
        index = request.session["photo_index"] + 1
        pit_photos = request.session["pit_photos"]

    # once we hit the last index without selecting a winner yet, redirect to a waiting page
    if len(pit_photos) == (index + 1):
        return redirect('waiting')

    request.session["photo_index"] = index
    pit_photo = PitPhoto.objects.get(id=pit_photos[index])

    return render(request, 'noshpit/list_photos.html', {'pit_photo': pit_photo})

def waiting(request):
    pit = Pit.objects.get(id=request.session["pit_id"])
    # find the user and inidicate that he has finished
    current_user = User.objects.get(id=request.session["user_id"])
    current_user.finished = True
    current_user.save()
    # check if all member of the pit have finished, if yes, redirect to no winner page
    pit_users = User.objects.filter(pit=pit)
    finished_pit_users = pit_users.filter(finished=True)
    if len(pit_users) == len(finished_pit_users):
        return redirect('no_winner')
    # check if winner was selected
    if pit.winner:
        return redirect('winner_detail')

    return render(request, 'noshpit/waiting.html', {})

def no_winner(request):
    pit = Pit.objects.get(id=request.session["pit_id"])
    # if no winner by voting, highest voted for location is recorded as a winner
    # location_votes = Vote.objects.filter(pit=request.session["pit_id"]).annotate(Count('user')).order_by('user__count')
    location_votes = Location.objects.filter(vote__pit=request.session["pit_id"]).annotate(Count("vote")).order_by("-vote__count")
    print(location_votes)
    winner = location_votes[0]
    print(winner)
    pit.winner = winner.location
    pit.save()

    return render(request, 'noshpit/no_winner.html', {})


def yes(request):
    # create a vote
    pit = Pit.objects.get(id=request.session["pit_id"])
    if pit.winner:
        return redirect('winner_detail')

    pit_photo = PitPhoto.objects.get(id=request.session["pit_photos"][request.session["photo_index"]])
    location = pit_photo.photo.location
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
    winner = location_votes.filter(user__count = num_users)

    if len(winner) > 0:
        pit.winner = location
        pit.save()

    return redirect('photos')

def winner_detail(request):
    pit = Pit.objects.get(id=request.session["pit_id"])
    winner = pit.winner
    url = 'https://maps.googleapis.com/maps/api/place'
    details_search = '/details/json?key='
    key = settings.PLACES_KEY
    placeid = '&placeid=' + winner.place_id
    response = requests.get(url + details_search + key + placeid)
    winner = json.loads(response.text)

    # check if winner is an object and not an error
    if winner["status"] != "OK":
        logging.info(winner["error_message"])
        # do something, because otherwise it will try to redirect with the worng winner object
    else:
        winner = Restaurant(winner)

    return render(request, 'noshpit/winner_detail.html', {'winner': winner})

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

    return photos
