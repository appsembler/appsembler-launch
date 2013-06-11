from django.contrib import admin
from .models import Deployment, Project


class ProjectModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'github_url', 'slug')

admin.site.register(Deployment)
admin.site.register(Project, ProjectModelAdmin)
