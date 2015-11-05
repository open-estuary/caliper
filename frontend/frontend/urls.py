from django.conf.urls import include, url
from django.contrib import admin

pollpatterns = [
    # Examples:
    url(r'^$', include('polls.urls', namespace="polls")),
    url(r'^polls/', include('polls.urls', namespace="polls")),
    url(r'^admin/', include(admin.site.urls)),
]

urlpatterns = pollpatterns
