from tastypie.authorization import Authorization
from tastypie.resources import ModelResource
from .models import Deployment, Project


class ProjectResource(ModelResource):
    class Meta:
        resource_name = 'projects'
        queryset = Project.objects.all()


class DeploymentResource(ModelResource):
    class Meta:
        resource_name = 'deployments'
        queryset = Deployment.objects.all()
        authorization = Authorization()
