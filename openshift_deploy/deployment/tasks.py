from celery import task

@task()
def deploy(deploy_instance):
    deploy_instance.deploy()
