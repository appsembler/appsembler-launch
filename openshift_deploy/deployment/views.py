from django.shortcuts import get_object_or_404
from django.views.generic import View, DetailView, ListView
from .api import ProjectResource
from .models import Deployment, Project


class DeployerView(View):
    def get_context_data(self, **kwargs):
        data = super(DeployerView, self).get_context_data(**kwargs)
        res = ProjectResource()
        objects = self.get_queryset()
        bundles = []

        for obj in objects:
            bundle = res.build_bundle(obj=obj, request=None)
            bundles.append(res.full_dehydrate(bundle, for_list=True))

        data["apps"] = res.serialize(None, bundles, 'application/json')
        data["app_count"] = len(objects)
        return data


class DeployerListView(DeployerView, ListView):
    template_name = 'deployment/deployer_list.html'

    def get_queryset(self):
        qs = Project.objects.all()
        if not self.request.user.is_superuser:
            qs = qs.filter(status='Active')
        return qs


class ProjectDeployerView(DeployerView, DetailView):
    template_name = 'deployment/deployer_detail.html'

    def get_queryset(self):
        return Project.objects.filter(slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        data = super(ProjectDeployerView, self).get_context_data(**kwargs)
        data['sizes'] = ('mini', 'small', 'medium', 'large')
        data['colors'] = (
            'grey',
            'blue',
            'green',
            'orange',
            'red',
            'black'
        )
        return data


class DeploymentDetailView(DetailView):
    def get_object(self, queryset=None):
        return get_object_or_404(Deployment, deploy_id=self.kwargs['deploy_id'])

    def get_context_data(self, **kwargs):
        data = super(DeploymentDetailView, self).get_context_data(**kwargs)
        obj = self.get_object()
        if obj.status == 'Completed':
            remaining = obj.get_remaining_seconds()
            data['remaining'] = remaining
            data['expiration'] = obj.expiration_datetime()
            data['percentage'] = (remaining / 3600.0) * 100
        return data
