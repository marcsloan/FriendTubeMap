from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from tubemap.models import TubeStations
from frontpage.models import TubeFriendMap
from frontpage.models import UserSession
from frontpage.models import ClusterRecord
import datetime
import frontpage.views
from django.template.loader import render_to_string
from tubemap.forms import FeedbackForm
from django.http import HttpResponseRedirect

def feedback(request):
    if hasattr(request, 'session') and not request.session.session_key:
        request.session.save()
        request.session.modified = True
    user = UserSession.objects.get_or_create(sessionID=request.session.session_key)[0]
    user.updateActivity()

    context = RequestContext(request)

    # A HTTP POST?
    if request.method == 'POST':
        form = FeedbackForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.
            form.save(commit=True)

            # Now call the index() view.
            # The user will be shown the homepage.
            return HttpResponseRedirect('/tubemap/')
        else:
            # The supplied form contained errors - just print them to the terminal.
            print form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        form = FeedbackForm()

    return render_to_response('tubemap/feedback.html', {'form': form}, context)


def info(request):
    if hasattr(request, 'session') and not request.session.session_key:
        request.session.save()
        request.session.modified = True
    user = UserSession.objects.get_or_create(sessionID=request.session.session_key)[0]
    user.updateActivity()

    context = RequestContext(request)

    return render_to_response('tubemap/info.html', dict(), context)


def tubemap(request):

    if hasattr(request, 'session') and not request.session.session_key:
        request.session.save()
        request.session.modified = True

    user = UserSession.objects.get_or_create(sessionID=request.session.session_key)[0]
    user.updateActivity()

    mostRecentClusteringType = user.lastClusterTechnique

    return renderMap(request, mostRecentClusteringType, user)

def reload(request):
    if hasattr(request, 'session') and not request.session.session_key:
        request.session.save()
        request.session.modified = True
    user = UserSession.objects.get_or_create(sessionID=request.session.session_key)[0]
    user.updateActivity()

    clusterRecord = ClusterRecord.objects.get_or_create(clusterType=user.lastClusterTechnique)[0]
    clusterRecord.timesChanged = clusterRecord.timesChanged + 1
    clusterRecord.save()

    mostRecentClusteringType = frontpage.views.handle_uploaded_file(user)

    return renderMap(request, mostRecentClusteringType, user)

def renderMap(request, clusterType, user):
    context = RequestContext(request)

    context_dict = getMapContextDict(request, clusterType, user)


    # Return a rendered response to send to the client.
    # We make use of the shortcut function to make our lives easier.
    # Note that the first parameter is the template we wish to use.
    return render_to_response('tubemap/tubemap.html', context_dict, context)

# #gets the HTML for the map and then saves it as a PNG
# def image(request):
#
#     user = UserSession.objects.get_or_create(sessionID=request.session.session_key)[0]
#     user.lastActivity = datetime.datetime.now()
#     user.save()
#
#
#     context_dict = getMapContextDict(request, user.lastClusterTechnique, user)
#
#     rendered = render_to_string('tubemap/tubemap.html', context_dict)




def getMapContextDict(request, clusterType, user):
    sessionID = request.session.session_key

    tubeStations = TubeStations.objects.all()

    context_dict = dict()
    for station in tubeStations:
        if TubeFriendMap.objects.filter(sessionID=user, station=station, clusterType=clusterType).exists():

            friendMap = TubeFriendMap.objects.get(sessionID=user, station=station, clusterType=clusterType)
            context_dict[station.stationNameVariable] = friendMap.name
        else:
            context_dict[station.stationNameVariable] = station.stationName
    return context_dict