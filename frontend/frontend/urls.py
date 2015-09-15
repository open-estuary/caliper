from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView
from django.contrib import admin

#homepatterns = patterns('homepage.views', 
#                            (r'^$', 'homepage'), )

#homepatterns += patterns('', (r'^favicon\.ico$',
#                        r'^one/$', RedirectView.as_view(url='/another/'),
#                        {'url': '/static/home/images/favicon.ico'}))

pollpatterns = [
    # Examples:
    url(r'^$', include('polls.urls', namespace="polls")),
    url(r'^polls/', include('polls.urls', namespace="polls")),
    url(r'^admin/', include(admin.site.urls)),
]

#urlpatterns = homepatterns + pollpatterns
urlpatterns = pollpatterns
