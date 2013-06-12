from django.conf.urls import include, patterns, url
from django.contrib import admin
from deployment.views import DeployerListView, ProjectDeployerView, DeploymentDetailView
from .api import v1_api

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^api/', include(v1_api.urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^deployment/(?P<deploy_id>[\w]+)/$', DeploymentDetailView.as_view(), name='deployment_detail'),
    url(r'^(?P<slug>[\w-]+)/$', ProjectDeployerView.as_view(), name='landing_page'),
    url(r'^$', DeployerListView.as_view(), name='main'),
)
