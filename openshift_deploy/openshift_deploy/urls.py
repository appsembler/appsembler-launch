from django.conf.urls import include, patterns, url
from django.contrib import admin
from deployment.views import MainView
from .api import v1_api

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^api/', include(v1_api.urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', MainView.as_view(), name='main'),  
)
