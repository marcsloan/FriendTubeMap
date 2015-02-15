from django.conf.urls import patterns, url
from tubemap import views

urlpatterns = patterns('',
        url(r'^$', views.tubemap, name='tubemap'), url(r'^reload/$', views.reload, name='reload'), url(r'^info.html$', views.info, name='info'),
        url(r'^feedback.html$', views.feedback, name='feedback'))