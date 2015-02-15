from django.contrib import admin
from tubemap.models import TubeStations
from tubemap.models import Feedback


class TubeStationsAdmin(admin.ModelAdmin):
    list_display = ('stationName', 'stationNameHTML', 'stationNameVariable')

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('whatLiked', 'whatWrong', 'generalComment')

admin.site.register(TubeStations, TubeStationsAdmin)
admin.site.register(Feedback, FeedbackAdmin)