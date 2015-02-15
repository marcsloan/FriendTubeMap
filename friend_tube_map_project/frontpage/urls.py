from django.conf.urls import patterns, url
from frontpage import views

urlpatterns = patterns('',
        url(r'^$', views.frontpage, name='frontpage'), url(r'^status/$', views.getStatus, name='status'))