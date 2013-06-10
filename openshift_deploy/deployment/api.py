from tastypie.authorization import Authorization
from tastypie import fields
from tastypie.resources import ModelResource
from .models import Deployment, Project


class ProjectResource(ModelResource):
    class Meta:
        resource_name = 'projects'
        queryset = Project.objects.all().order_by('name')
        limit = 0
        authorization = Authorization()


class DeploymentResource(ModelResource):
    project = fields.ForeignKey(ProjectResource, 'project')

    class Meta:
        resource_name = 'deployments'
        queryset = Deployment.objects.all()
        authorization = Authorization()
        always_return_data = True
