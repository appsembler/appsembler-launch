import logging
import requests
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from celery import task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@task()
def deploy(deploy_instance):
    deploy_instance.deploy()


@task()
def destroy_expired_apps():
    # protection against circular imports
    from .models import Deployment
    expired = Deployment.objects.filter(expiration_time__lt=timezone.now(),
                                        status='Completed')
    if expired:
        for app in expired:
            app.status = 'Expired'
            app.save()
            r = requests.delete(
                "{0}/api/v1/containers/{1}/?username={2}&api_key={3}".format(
                    settings.SHIPYARD_HOST,
                    app.remote_container_id,
                    settings.SHIPYARD_USER,
                    settings.SHIPYARD_KEY
                ),
            )
            r = requests.delete(
                "{0}/api/v1/applications/{1}/?username={2}&api_key={3}".format(
                    settings.SHIPYARD_HOST,
                    app.remote_app_id,
                    settings.SHIPYARD_USER,
                    settings.SHIPYARD_KEY
                ),
            )


@task()
def app_expiring_soon_reminder():
    # protection against circular imports
    from .models import Deployment

    #finds deployed apps that have less than 15mins left and
    #haven't been notified yet
    t = timezone.now() + timedelta(minutes=15)
    expiring_soon = Deployment.objects.filter(expiration_time__lt=t,
                                              reminder_mail_sent=False)

    for app in expiring_soon:
        app.send_reminder_email()
        app.reminder_mail_sent = True
        app.save()
