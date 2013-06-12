# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Deployment.launch_date'
        db.delete_column(u'deployment_deployment', 'launch_date')

        # Adding field 'Deployment.launch_time'
        db.add_column(u'deployment_deployment', 'launch_time',
                      self.gf('django.db.models.fields.DateTimeField')(null=True),
                      keep_default=False)

        # Adding field 'Deployment.created'
        db.add_column(u'deployment_deployment', 'created',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime(2013, 6, 12, 0, 0), blank=True),
                      keep_default=False)


        # Changing field 'Project.slug'
        db.alter_column(u'deployment_project', 'slug', self.gf('django.db.models.fields.SlugField')(max_length=40, null=True))

    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'Deployment.launch_date'
        raise RuntimeError("Cannot reverse this migration. 'Deployment.launch_date' and its values cannot be restored.")
        # Deleting field 'Deployment.launch_time'
        db.delete_column(u'deployment_deployment', 'launch_time')

        # Deleting field 'Deployment.created'
        db.delete_column(u'deployment_deployment', 'created')


        # Changing field 'Project.slug'
        db.alter_column(u'deployment_project', 'slug', self.gf('django.db.models.fields.SlugField')(default='', max_length=40))

    models = {
        u'deployment.deployment': {
            'Meta': {'object_name': 'Deployment'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deploy_id': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'launch_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'deployments'", 'to': u"orm['deployment.Project']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'Deploying'", 'max_length': '50'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'deployment.project': {
            'Meta': {'ordering': "['name']", 'object_name': 'Project'},
            'database': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'github_url': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        }
    }

    complete_apps = ['deployment']