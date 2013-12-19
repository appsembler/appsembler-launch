import datetime
import json
import logging
import pusher
import requests
import time
from urlparse import urlparse
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone
from customerio import CustomerIO
from model_utils.fields import StatusField
from model_utils import Choices
from .tasks import deploy

logger = logging.getLogger(__name__)


class Project(models.Model):
    STATUS = Choices('Active', 'Hidden', 'Inactive')

    name = models.CharField(max_length=100)
    github_url = models.CharField(max_length=200)
    image_name = models.CharField(max_length=300)
    ports = models.CharField(max_length=300, help_text="Internally exposed port, example: 80")
    env_vars = models.CharField(max_length=500, blank=True,
                                help_text="Space separated environment variables, example: key1=val1 key2=val2")
    trial_duration = models.IntegerField(default=60, help_text="Trial duration in minutes")
    slug = models.SlugField(max_length=40, editable=False, blank=True, null=True)
    status = StatusField(default=STATUS.Inactive)
    default_username = models.CharField(max_length=30, blank=True)
    default_password = models.CharField(max_length=30, blank=True)
    survey_form_url = models.URLField(blank=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        super(Project, self).save(*args, **kwargs)

    def landing_page_url(self):
        return reverse('landing_page', kwargs={'slug': self.slug})


class Deployment(models.Model):
    STATUS_CHOICES = (
        ('Deploying', 'Deploying'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
        ('Expired', 'Expired')
    )
    project = models.ForeignKey(Project, related_name='deployments')
    url = models.CharField(max_length=200)
    email = models.EmailField()
    deploy_id = models.CharField(max_length=100)
    remote_container_id = models.IntegerField(default=0)
    remote_app_id = models.IntegerField(default=0)
    launch_time = models.DateTimeField(blank=True, null=True)
    expiration_time = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES,
                              default='Deploying')
    reminder_mail_sent = models.BooleanField()

    def __unicode__(self):
        return self.deploy_id

    def save(self, *args, **kwargs):
        """
        Save the object with the "deploying" status to the DB to get
        the ID, and use that in a celery deploy task
        """
        if not self.id:
            self.status = 'Deploying'
        super(Deployment, self).save(*args, **kwargs)
        if self.status == 'Deploying':
            deploy.delay(self)

    def get_remaining_seconds(self):
        if self.expiration_time and self.expiration_time > timezone.now():
            diff = self.expiration_time - timezone.now()
            return diff.seconds
        return 0

    def get_remaining_minutes(self):
        if self.expiration_time and self.expiration_time > timezone.now():
            diff = self.expiration_time - timezone.now()
            remaining_minutes = diff.seconds / 60
            return remaining_minutes
        return 0
    get_remaining_minutes.short_description = 'Minutes remaining'

    def expiration_datetime(self):
        return self.launch_time + datetime.timedelta(minutes=self.project.trial_duration)

    def deploy(self):
        instance = self._get_pusher_instance()
        instance[self.deploy_id].trigger('info_update', {
            'message': "Creating a new container...",
            'percent': 30
        })
        headers = {
            'content-type': 'application/json'
        }
        # run the container
        payload = {
            "image": self.project.image_name,
            "hosts": ["/api/v1/hosts/1/"],
            "ports": self.project.ports.split(' '),
            "description": self.email or "",
            "environment": self.project.env_vars.split(' ')
            #"wait": 30
        }
        r = requests.post(
            "{0}/api/v1/containers/?username={1}&api_key={2}".format(settings.SHIPYARD_HOST, settings.SHIPYARD_USER, settings.SHIPYARD_KEY),
            data=json.dumps(payload),
            headers=headers
        )
        if r.status_code == 201:
            container_uri = urlparse(r.headers['location']).path
            self.remote_container_id = container_uri.split('/')[-2]

            # create the app (for dynamic routing)
            instance[self.deploy_id].trigger('info_update', {
                'message': "Assigning an URL to the app...",
                'percent': 60
            })
            domain_name = "{0}.demo.appsembler.com".format(self.deploy_id)
            payload = {
                "name": self.deploy_id,
                "description": "{0} for {1}".format(self.project.name, self.email),
                "domain_name": domain_name,
                "backend_port": self.project.ports,
                "protocol": "https" if "443" in self.project.ports else "http",
                "containers": [container_uri]
            }
            r = requests.post(
                "{0}/api/v1/applications/?username={1}&api_key={2}".format(settings.SHIPYARD_HOST, settings.SHIPYARD_USER, settings.SHIPYARD_KEY),
                data=json.dumps(payload),
                headers=headers
            )
            if r.status_code == 201:
                app_uri = urlparse(r.headers['location']).path
                self.remote_app_id = app_uri.split('/')[-2]
        status = r.status_code
        time.sleep(1)
        instance[self.deploy_id].trigger('info_update', {
            'message': "Getting information...",
            'percent': 90
        })
        time.sleep(1)
        if status == 201:
            scheme = "https" if "443" in self.project.ports else "http"
            app_url = "{0}://{1}".format(scheme, domain_name)
            self.url = app_url
            self.status = 'Completed'
            self.launch_time = timezone.now()
            self.expiration_time = self.expiration_datetime()
            instance[self.deploy_id].trigger('deployment_complete', {
                'app_name': self.project.name,
                'message': "Deployment complete!",
                'app_url': app_url,
                'username': self.project.default_username,
                'password': self.project.default_password
            })
            if self.email:
                cio = CustomerIO(settings.CUSTOMERIO_SITE_ID, settings.CUSTOMERIO_API_KEY)
                cio.track(customer_id=self.email,
                          name='app_deploy_complete',
                          app_url=app_url,
                          app_name=self.project.name,
                          status_url="http://launcher.appsembler.com" + reverse('deployment_detail', kwargs={'deploy_id': self.deploy_id}),
                          username=self.project.default_username,
                          password=self.project.default_password
                )
        else:
            self.status = 'Failed'
            error_log = DeploymentErrorLog(deployment=self, http_status=status, error_log=r.text)
            error_log.save()
            instance[self.deploy_id].trigger('deployment_failed', {
                'message': "Deployment failed!",
            })
        self.save()

    def send_reminder_email(self):
        if self.email:
            cio = CustomerIO(settings.CUSTOMERIO_SITE_ID, settings.CUSTOMERIO_API_KEY)
            cio.track(
                customer_id=self.email,
                name='app_expiring_soon',
                app_url=self.url,
                status_url="http://launcher.appsembler.com" + reverse('deployment_detail', kwargs={'deploy_id': self.deploy_id}),
                remaining_minutes=self.get_remaining_minutes(),
                expiration_time=timezone.localtime(self.expiration_time).isoformat()
            )

    def _get_pusher_instance(self):
        push = pusher.Pusher(
            app_id=settings.PUSHER_APP_ID,
            key=settings.PUSHER_APP_KEY,
            secret=settings.PUSHER_APP_SECRET
        )
        return push


class DeploymentErrorLog(models.Model):
    deployment = models.OneToOneField(Deployment, related_name='error_log')
    http_status = models.CharField(max_length=3)
    error_log = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
