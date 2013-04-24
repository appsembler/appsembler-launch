from exceptions import Exception
from django.conf import settings
from django.db import models
from oshift import Openshift


class DeploymentException(Exception):
    pass


class Project(models.Model):
    name = models.CharField(max_length=100)
    github_url = models.CharField(max_length=200)
    version = models.CharField(max_length=300)
    database = models.CharField(max_length=300, blank=True)

    def __unicode__(self):
        return self.name

    def cartridges_list(self):
        complete_list = self.version + "," + self.database
        return [v.strip() for v in complete_list.split(',')]


class Deployment(models.Model):
    project = models.ForeignKey(Project, related_name='deployments')
    url = models.CharField(max_length=200)
    email = models.EmailField()
    deploy_id = models.CharField(max_length=100)
    launch_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)

    def __unicode__(self):
        return self.deploy_id

    def save(self, *args, **kwargs):
        try:
            data = self.deploy()
        except DeploymentException:
            raise

        self.url = data['app_url']
        self.deploy_id = self.project.name + data['uuid']
        self.status = data['status']
        super(Deployment, self).save(*args, **kwargs)

    def deploy(self):
        li = Openshift(
            host=settings.OPENSHIFT_HOST,
            user=settings.OPENSHIFT_USER,
            passwd=settings.OPENSHIFT_PASSWORD,
            debug=settings.OPENSHIFT_DEBUG,
            verbose=settings.OPENSHIFT_VERBOSE
        )
        status, res = li.app_create(
            app_name=self.project.name,
            app_type=self.project.cartridges_list(),
            init_git_url=self.project.github_url
        )

        if status == 201:
            data = res()
            print status
            print data
            return {
                'app_url': data['data'].get('app_url'),
                'status': data.get('status'),
                'uuid': data['data'].get('uuid'),
            }
        else:
            raise DeploymentException(res()['messages'][0]['text'])
