import logging
from datetime import datetime, timedelta
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
	expired = Deployment.objects.filter(expiration_time__lt=datetime.now()).exclude(
		status='Expired')
	if expired:
		oshift = expired[0]._get_openshift_instance()
		for app in expired:
			app.status = 'Expired'
			app.save()
			oshift.app_delete(app_name=app.deploy_id)
