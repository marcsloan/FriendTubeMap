from django.db import models

from django.db import models
import os
from tubemap.models import TubeStations
from django.conf import settings
import datetime

def get_saving_path(path):
    def wrapper(instance, filename):
        return os.path.join(path, '%s-graph.gml' % instance.sessionID)
    return wrapper

class SocialData(models.Model):
    sessionID = models.CharField(max_length=128, unique=False)
    docfile = models.FileField(upload_to=get_saving_path(settings.SOCIAL_FILE_SUFFIX))


class UserSession(models.Model):

    sessionID = models.CharField(max_length=128)
    lastActivity = models.DateField(default=datetime.datetime.now())
    lastClusterTechnique = models.IntegerField(default=-1)
    status = models.CharField(max_length=300, default='')

    def __unicode__(self):
        return self.sessionID + ' ' + str(self.lastActivity) + ' ' + str(self.lastClusterTechnique) + ' ' + str(self.status)

    def updateActivity(self):
        self.lastActivity = datetime.datetime.now()
        self.save()

    def setStatus(self, status):
        self.status = status
        self.save()


class TubeFriendMap(models.Model):

    #sessionID = models.CharField(max_length=128)
    sessionID = models.ForeignKey(UserSession)
    name = models.CharField(max_length=128)
    station = models.ForeignKey(TubeStations)
    clusterType = models.IntegerField(default=-1)

    def __unicode__(self):
        return str(self.sessionID) + ' ' + self.name + ' ' + str(self.station)

class ClusterRecord(models.Model):
    clusterType = models.IntegerField(unique=True)
    timesUsed = models.IntegerField(default=0)
    timesChanged = models.IntegerField(default=0)

    def __unicode__(self):
        return str(self.clusterType) + ' ' + str(self.timesUsed) + ' ' + str(self.timesChanged)


    def updateTimesUsed(self):
        self.timesUsed = self.timesUsed + 1
        self.save()


