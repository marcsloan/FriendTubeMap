from django.contrib import admin
from frontpage.models import TubeFriendMap
from frontpage.models import UserSession
from frontpage.models import ClusterRecord

class FrontPageAdmin(admin.ModelAdmin):
    list_display = ('sessionID', 'name', 'station', 'clusterType')

class FrontPageUserAdmin(admin.ModelAdmin):
    list_display = ('sessionID', 'lastActivity', 'lastClusterTechnique', 'status')

class FrontPageClusterAdmin(admin.ModelAdmin):
    list_display = ('clusterType', 'timesUsed', 'timesChanged')

admin.site.register(TubeFriendMap, FrontPageAdmin)
admin.site.register(UserSession, FrontPageUserAdmin)
admin.site.register(ClusterRecord, FrontPageClusterAdmin)