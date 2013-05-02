import django_rq
import pusher
import time
from django.conf import settings
from django.core.mail import send_mail
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
    STATUS_CHOICES = (
        ('Deploying', 'Deploying'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    )
    project = models.ForeignKey(Project, related_name='deployments')
    url = models.CharField(max_length=200)
    email = models.EmailField()
    deploy_id = models.CharField(max_length=100)
    launch_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES,
                              default='Deploying')

    def __unicode__(self):
        return self.deploy_id

    def save(self, *args, **kwargs):
        if not self.id:
            django_rq.enqueue(self.deploy)
        self.status = 'Deploying'
        super(Deployment, self).save(*args, **kwargs)

    def deploy(self):
        instance = pusher.Pusher(
            app_id=settings.PUSHER_APP_ID,
            key=settings.PUSHER_APP_KEY,
            secret=settings.PUSHER_APP_SECRET
        )
        li = Openshift(
            host=settings.OPENSHIFT_HOST,
            user=settings.OPENSHIFT_USER,
            passwd=settings.OPENSHIFT_PASSWORD,
            debug=settings.OPENSHIFT_DEBUG,
            verbose=settings.OPENSHIFT_VERBOSE
        )
        instance[self.deploy_id].trigger('info_update', {
            'message': "Creating a new app...",
            'percent': 30
        })
        status, res = li.app_create(
            app_name=self.deploy_id,
            app_type=self.project.cartridges_list(),
            init_git_url=self.project.github_url
        )
        instance[self.deploy_id].trigger('info_update', {
            'message': "Getting results...",
            'percent': 60
        })
        data = res()
        print data
        if status == 201:
            app_url = data['data'].get('app_url')
            self.status = 'Completed'
            self.app_url = app_url
            instance[self.deploy_id].trigger('deployment_complete', {
                'message': "Deployment complete!",
                'app_url': app_url
            })
            if self.email:
                send_mail('Deployment successful', 'Application URL: {0}'.format(app_url),
                          'info@deployer.com', [self.email], fail_silently=True)
        else:
            self.status = 'Failed'
            instance[self.deploy_id].trigger('deployment_failed', {
                'message': "Deployment failed!",
                'details': data['messages'][0]['text']
            })
        super(Deployment, self).save()
