from django.db import models

class TubeStations(models.Model):
    stationName = models.CharField(max_length=128, unique=True)
    stationNameHTML = models.CharField(max_length=128)
    stationNameVariable= models.CharField(max_length=128)

    def __unicode__(self):
        return self.stationName

class Feedback(models.Model):

    whatLiked = models.CharField(max_length=2000)
    whatWrong = models.CharField(max_length=2000)
    generalComment = models.CharField(max_length=2000)

    def __unicode__(self):
        return self.whatLiked



