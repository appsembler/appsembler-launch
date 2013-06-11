# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Project'
        db.create_table(u'deployment_project', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('github_url', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('database', self.gf('django.db.models.fields.CharField')(max_length=300, blank=True)),
        ))
        db.send_create_signal(u'deployment', ['Project'])

        # Adding model 'Deployment'
        db.create_table(u'deployment_deployment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='deployments', to=orm['deployment.Project'])),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('deploy_id', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('launch_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='Deploying', max_length=50)),
        ))
        db.send_create_signal(u'deployment', ['Deployment'])


    def backwards(self, orm):
        # Deleting model 'Project'
        db.delete_table(u'deployment_project')

        # Deleting model 'Deployment'
        db.delete_table(u'deployment_deployment')


    models = {
        u'deployment.deployment': {
            'Meta': {'object_name': 'Deployment'},
            'deploy_id': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'launch_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'deployments'", 'to': u"orm['deployment.Project']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'Deploying'", 'max_length': '50'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'deployment.project': {
            'Meta': {'object_name': 'Project'},
            'database': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'github_url': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        }
    }

    complete_apps = ['deployment']