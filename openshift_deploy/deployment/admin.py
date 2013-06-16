from django.contrib import admin
from .models import Deployment, Project


class ProjectModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'github_url', 'slug', 'status')
    list_filter = ('status',)


class DeploymentModelAdmin(admin.ModelAdmin):
    list_display = ('deploy_id', 'project', 'deployed_app_url', 'email',
                    'status', 'launch_time', 'get_remaining_minutes')
    list_filter = ('status', 'project__name')
    ordering = ['-launch_time', 'project']

    def deployed_app_url(self, obj):
        return '<a href="{0}">{0}</a>'.format(obj.url)
    deployed_app_url.short_description = "App URL"
    deployed_app_url.allow_tags = True

admin.site.register(Deployment, DeploymentModelAdmin)
admin.site.register(Project, ProjectModelAdmin)
