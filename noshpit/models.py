from django.db import models

class Location(models.Model):
    place_id = models.CharField(max_length=300, unique=True)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Photo(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    url = models.CharField(max_length=300, unique=True)

class Pit(models.Model):
    token = models.CharField(max_length=5)
    winner = models.ForeignKey(Location, blank=True, null=True)

class PitPhoto(models.Model):
    photo = models.ForeignKey(Photo)
    pit = models.ForeignKey(Pit)

class User(models.Model):
    pit = models.ForeignKey(Pit, on_delete=models.CASCADE)

class Vote(models.Model):
    pit = models.ForeignKey(Pit)
    user = models.ForeignKey(User)
    location = models.ForeignKey(Location)

    def __str__(self):
        return f"{self.location.name} : {self.user.id}"

    class Meta:
        unique_together = ("pit", "user", "location")
