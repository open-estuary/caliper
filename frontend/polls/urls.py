#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.conf import settings

from . import views

urlpatterns = [
        # ex:  /polls/
        url(r'^$', views.index, name='index'),
        # for Performance
        url(r'algorithm.html/$', views.algorithm, name='algorithm'),
        url(r'cpu_sincore.html/$', views.cpu_sincore, name='cpu_sincore'),
        url(r'cpu_multicore.html/$', views.cpu_multicore, name='cpu_multicore'),
        url(r'storage.html/$', views.storage, name='storage'),
        url(r'latency.html/$', views.latency, name='latency'),
        url(r'memory.html/$', views.memory, name='memory'),
        url(r'network.html/$', views.network, name='network'),
        #url(r'io/$', views.io, name='io'),
        url(r'application.html/$', views.application, name='application'),
        # for Functional
        url(r'kernel.html/$', views.kernel, name='kernel'),
        url(r'debug.html/$', views.debug, name='debug'),
        url(r'peripheral.html/$', views.peripheral, name='peripheral'),
        ##
        url(r'static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.STATIC_ROOT}, name='static'),
]
