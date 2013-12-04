import datetime
import json
import logging
import pusher
import requests
import time
from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from django.utils import timezone
from customerio import CustomerIO
from model_utils.fields import StatusField
from model_utils import Choices
from oshift import Openshift, OpenShiftException
from requests.exceptions import SSLError
from deployment.tasks import deploy

logger = logging.getLogger(__name__)


class Project(models.Model):
    STATUS = Choices('Active', 'Inactive')

    name = models.CharField(max_length=100)
    github_url = models.CharField(max_length=200)
    image_name = models.CharField(max_length=300)
    ports = models.CharField(max_length=300, help_text="List of exposed ports separated by spaces, example: 80 22")
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
        return self.launch_time + datetime.timedelta(minutes=60)

    def deploy(self):
        instance = self._get_pusher_instance()
        instance[self.deploy_id].trigger('info_update', {
            'message': "Creating a new container...",
            'percent': 30
        })
        message = None
        log_error = False
        try:
            headers = {
                'content-type': 'application/json'
            }
            # run the container
            payload = {
                "image": self.project.image_name,
                "hosts":["/api/v1/hosts/1/"],
                "ports": self.project.ports.split(' ')
            }
            r = requests.post(
                "{0}/api/v1/containers/?username={1}&api_key={2}".format(settings.SHIPYARD_HOST, settings.SHIPYARD_USER, settings.SHIPYARD_KEY),
                data=json.dumps(payload),
                headers=headers
            )
            if r.status_code == 201:
                data = json.loads(r.text)
                container_uri = data['resource_uri']

            # create the app (for dynamic routing)
            instance[self.deploy_id].trigger('info_update', {
                'message': "Assigning an URL to the app...",
                'percent': 60
            })
            domain_name = "{0}.app.appsembler.com".format(self.deploy_id)
            payload = {
                "name": self.deploy_id,
                "description": self.project.name,
                "domain_name": domain_name,
                "backend_port": 80,
                "protocol": "http",
                "containers":[container_uri]
            }
            r = requests.post(
                "{0}/api/v1/applications/?username={1}&api_key={2}".format(settings.SHIPYARD_HOST, settings.SHIPYARD_USER, settings.SHIPYARD_KEY),
                data=json.dumps(payload),
                headers=headers
            )
            status = r.status_code
        except (SSLError, ValueError) as e:
            # workaround to be able to log errors when the deployment fails
            #if e.__class__ == docker.client.APIError:
            #    log_error = True
            status = 500
            message = "A critical error has occured."
            logger.error("Critical error has occured during deployment".format(self.project.name),
                exc_info=True,
                extra={
                    'user_email': self.email,
                    'project_name': self.project.name,
                }
            )
        instance[self.deploy_id].trigger('info_update', {
            'message': "Getting information...",
            'percent': 90
        })
        time.sleep(3)
        if status != 500:
            app_url = "http://{0}".format(domain_name)
            self.url = app_url
            self.status = 'Completed'
            self.launch_time = timezone.now()
            self.expiration_time = self.launch_time + datetime.timedelta(minutes=60)
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
                          status_url="http://launch.appsembler.com/" + reverse('deployment_detail', kwargs={'deploy_id': self.deploy_id}),
                          username=self.project.default_username,
                          password=self.project.default_password
                )
        else:
            self.status = 'Failed'
            if log_error:
                error_log = DeploymentErrorLog(deployment=self, http_status=status, error_log="error")
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
                status_url= "http://launch.appsembler.com/" + reverse('deployment_detail', kwargs={'deploy_id': self.deploy_id}),
                remaining_minutes=self.get_remaining_minutes(),
                expiration_time=timezone.localtime(self.expiration_time)
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
