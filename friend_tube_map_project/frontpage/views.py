from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from frontpage.forms import UploadFileForm
from frontpage.models import SocialData
from django.http import HttpResponseRedirect
from frontpage.processSocialData import ProcessSocial
from frontpage.models import TubeFriendMap
from frontpage.models import UserSession
from frontpage.models import ClusterRecord
from tubemap.models import TubeStations
import random
import datetime

def frontpage(request):

    context = RequestContext(request)
    if hasattr(request, 'session') and not request.session.session_key:
        request.session.save()
        request.session.modified = True
    sessionID=request.session.session_key

    user = UserSession.objects.get_or_create(sessionID=request.session.session_key)[0]
    user.updateActivity()
    user.setStatus('')

    #if the user is uploading the file
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            user.setStatus('Just uploading your social data, should only take a moment')
            newdoc = SocialData(docfile = request.FILES['docfile'], sessionID=request.session.session_key)
            newdoc.save()

            user.setStatus('Just finished uploading your data, let\'s take a look at it')
            print user.status
            handle_uploaded_file(user, newdoc.docfile)

            # Redirect to the document list after POST
            return HttpResponseRedirect('/tubemap/')
        else:
            user.setStatus('Uh oh, uploading your data didn\'t work that time, try giving it another go.')
    else:
        form = UploadFileForm()

    return render_to_response('frontpage/frontpage.html', {'form': form}, context)


def handle_uploaded_file(user, f=None):
    social = ProcessSocial(user)
    if f==None:
        social.readFile(user.sessionID)
    else:
        social.processFile(f)

    techniquesUsed = TubeFriendMap.objects.filter(sessionID=user).values('clusterType').distinct()
    #make sure to try a new clustering style
    techniques = []
    for type in techniquesUsed:
        techniques.append(type['clusterType'])

    (randomMapping, clusterType) = social.getRandomMapping(techniques)

    user.setStatus('Phew that took a lot of work, time to draw your social underground map for you')

    user.lastClusterTechnique = clusterType
    user.save()

    clusterRecord = ClusterRecord.objects.get_or_create(clusterType=clusterType)[0]
    clusterRecord.updateTimesUsed()

    #save the tube station mapping to the database
    for station in randomMapping:
        stationKey = TubeStations.objects.get(stationName=station.encode("ascii"))
        friend = TubeFriendMap.objects.get_or_create(sessionID=user, station=stationKey, clusterType=clusterType)[0]
        friend.name = randomMapping[station]
        friend.save()

    return clusterType

def getStatus(request):
    if hasattr(request, 'session') and not request.session.session_key:
        request.session.save()
        request.session.modified = True
    user = UserSession.objects.get_or_create(sessionID=request.session.session_key)[0]
    user.updateActivity()
    if user.status == '':
        user.setStatus('Uploading Social Data')
    return HttpResponse(user.status)