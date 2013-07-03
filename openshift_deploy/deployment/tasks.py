import logging
from datetime import datetime, timedelta
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
		oshift = expired[0]._get_openshift_instance()
		for app in expired:
			app.status = 'Expired'
			app.save()
			oshift.app_delete(app_name=app.deploy_id)

@task()
def app_expiring_soon_reminder():
	# protection against circular imports
	from .models import Deployment
	
	# finds deployed apps that have less than 15mins left and
	# haven't been notified yet
	t = timezone.now() + timedelta(minutes=15)
	expiring_soon = Deployment.objects.filter(expiration_time__lt=t,
											  reminder_mail_sent=False)

	for app in expiring_soon:
		app.send_reminder_email()
		app.reminder_mail_sent = True
		app.save()
