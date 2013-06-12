from django.shortcuts import get_object_or_404
from django.views.generic import View, DetailView, ListView
from .api import ProjectResource
from .models import Deployment, Project


class DeployerView(View):
    template_name = "deployer.html"

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
    def get_queryset(self):
        return Project.objects.all()


class ProjectDeployerView(DeployerView, DetailView):
    def get_queryset(self):
        return Project.objects.filter(slug=self.kwargs['slug'])


class DeploymentDetailView(DetailView):
    def get_object(self, queryset=None):
        return get_object_or_404(Deployment, deploy_id=self.kwargs['deploy_id'])

    def get_context_data(self, **kwargs):
        data = super(DeploymentDetailView, self).get_context_data(**kwargs)
        obj = self.get_object()
        if obj.status == 'Completed':
            remaining = obj.get_remaining_minutes()
            data['remaining'] = remaining
            data['percentage'] = (remaining / 60.0) * 100
        return data
