#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    E-mail    :    wu.wu@hisilicon.com
#    Data      :    2015-06-02 17:22:02
#    Desc      :
from django.conf.urls import url
from django.conf import settings

from . import views

urlpatterns = [
        # ex:  /polls/
        url(r'^$', views.index, name='index'),
        # for Performance
        url(r'algorithm/$', views.algorithm, name='algorithm'),
        url(r'cpu/$', views.cpu, name='cpu'),
        url(r'disk/$', views.disk, name='disk'),
        url(r'latency/$', views.latency, name='latency'),
        url(r'memory/$', views.memory, name='memory'),
        url(r'network/$', views.network, name='network'),
        url(r'io/$', views.io, name='io'),
        url(r'application/$', views.application, name='application'),
        # for Functional
        url(r'kernel/$', views.kernel, name='kernel'),
        url(r'debug/$', views.debug, name='debug'),
        url(r'peripheral/$', views.peripheral, name='peripheral'),
        ##
        url(r'static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.STATIC_ROOT}, name='static'),
]
