openshift_deploy
================

Small exercise to create a widget that lets a user select an app from a dropdown menu, and deploy it to Redhat OpenShift PaaS

Needed:
running Redis server on port 6379 with no password
OpenShift account
Pusher account
(optionally) mail server account

Instructions:
  python manage.py runserver
  python manage.py rqworker default
