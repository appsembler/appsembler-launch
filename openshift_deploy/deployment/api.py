from tastypie.resources import ModelResource
from .models import Deployment, Project


class ProjectResource(ModelResource):
    class Meta:
        queryset = Project.objects.all()


class DeploymentResource(ModelResource):
    class Meta:
        queryset = Deployment.objects.all()
