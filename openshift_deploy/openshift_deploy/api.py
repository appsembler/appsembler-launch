from tastypie.api import Api
from deployment.api import DeploymentResource, ProjectResource


v1_api = Api(api_name='v1')
v1_api.register(DeploymentResource())
v1_api.register(ProjectResource())
