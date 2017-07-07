from django.db import models

class Location(models.Model):
    place_id = models.CharField(max_length=300)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Photo(models.Model):
    location = models.ForeignKey(Location)
    url = models.CharField(max_length=300)

class Pit(models.Model):
    token = models.CharField(max_length=5)

class User(models.Model):
    pass

class Vote(models.Model):
    pit = models.ForeignKey(Pit)
    user = models.ForeignKey(User)
    location = models.ForeignKey(Location)
