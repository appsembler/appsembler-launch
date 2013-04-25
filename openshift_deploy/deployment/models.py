import random
import string
from django.conf import settings
from django.db import models
from oshift import Openshift


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
        data = self.deploy()

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
        random_string = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(10))
        status, res = li.app_create(
            app_name="{0}_{1}".format(self.project.name, random_string),
            app_type=self.project.cartridges_list(),
            init_git_url=self.project.github_url
        )

        data = res()
        return_data = {}
        if status == 201:
            print data
            return_data['success'] = True
            return_data['success'] = data['data'].get('app_url')
            return_data['success'] = data.get('status')
        else:
            return_data['success'] = False
            return_data['message'] = data['messages'][0]['text']
        return return_data
