from django.db import models


class Project(models.Model):
    name = models.CharField(max_length=100)
    github_url = models.CharField(max_length=200)
    version = models.CharField(max_length=300)
    database = models.CharField(max_length=300, blank=True)

    def __unicode__(self):
        return self.name


class Deployment(models.Model):
    project = models.ForeignKey(Project, related_name='deployments')
    url = models.CharField(max_length=200)
    email = models.EmailField()
    deploy_id = models.CharField(max_length=100)
    launch_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)

    def __unicode__(self):
        return u"{0}: {1}".format(self.project.name, self.deploy_id)
