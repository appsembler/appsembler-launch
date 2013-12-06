# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Deployment.remote_container_id'
        db.add_column(u'deployment_deployment', 'remote_container_id',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Deployment.remote_app_id'
        db.add_column(u'deployment_deployment', 'remote_app_id',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Deployment.remote_container_id'
        db.delete_column(u'deployment_deployment', 'remote_container_id')

        # Deleting field 'Deployment.remote_app_id'
        db.delete_column(u'deployment_deployment', 'remote_app_id')


    models = {
        u'deployment.deployment': {
            'Meta': {'object_name': 'Deployment'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deploy_id': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'expiration_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'launch_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'deployments'", 'to': u"orm['deployment.Project']"}),
            'reminder_mail_sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'remote_app_id': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'remote_container_id': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'Deploying'", 'max_length': '50'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'deployment.deploymenterrorlog': {
            'Meta': {'object_name': 'DeploymentErrorLog'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deployment': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'error_log'", 'unique': 'True', 'to': u"orm['deployment.Deployment']"}),
            'error_log': ('django.db.models.fields.TextField', [], {}),
            'http_status': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'deployment.project': {
            'Meta': {'ordering': "['name']", 'object_name': 'Project'},
            'default_password': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'default_username': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'github_url': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_name': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'ports': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'status': ('model_utils.fields.StatusField', [], {'default': "'Inactive'", 'max_length': '100', u'no_check_for_status': 'True'}),
            'survey_form_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        }
    }

    complete_apps = ['deployment']