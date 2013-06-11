from django.views.generic import View, DetailView, ListView
from .api import ProjectResource
from .models import Project


class DeployerView(View):
    template_name = "main.html"

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
