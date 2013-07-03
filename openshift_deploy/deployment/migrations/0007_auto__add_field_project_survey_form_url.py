# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Project.survey_form_url'
        db.add_column(u'deployment_project', 'survey_form_url',
                      self.gf('django.db.models.fields.URLField')(default='', max_length=200, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Project.survey_form_url'
        db.delete_column(u'deployment_project', 'survey_form_url')


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
            'status': ('django.db.models.fields.CharField', [], {'default': "'Deploying'", 'max_length': '50'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'deployment.project': {
            'Meta': {'ordering': "['name']", 'object_name': 'Project'},
            'database': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'default_password': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'default_username': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'github_url': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'status': ('model_utils.fields.StatusField', [], {'default': "'Inactive'", 'max_length': '100', u'no_check_for_status': 'True'}),
            'survey_form_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        }
    }

    complete_apps = ['deployment']