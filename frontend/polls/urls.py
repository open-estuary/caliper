#!/usr/bin/env python
# -*- coding: utf-8 -*-
#                      
#    E-mail    :    wu.wu@hisilicon.com 
#    Data      :    2015-06-02 17:22:02
#    Desc      :
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
        # ex:  /polls/
        url(r'^$', views.index, name='index'),
        url(r'algorithm/$', views.algorithm, name='algorithm' ),
        url(r'cpu/$', views.cpu, name='cpu'),
        url(r'disk/$', views.disk, name='disk'),
        url(r'latency/$', views.latency, name='latency'),
        url(r'memory/$', views.memory, name='memory'),
        url(r'static/(?P<path>.*)$', 'django.views.static.serve', 
            {'document_root': settings.STATIC_ROOT}, name='static'),
        ]

