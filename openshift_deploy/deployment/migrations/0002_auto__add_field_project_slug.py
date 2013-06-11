# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Project.slug'
        db.add_column(u'deployment_project', 'slug',
                      self.gf('django.db.models.fields.SlugField')(null=True, default='', max_length=40),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Project.slug'
        db.delete_column(u'deployment_project', 'slug')


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
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '40', 'blank': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        }
    }

    complete_apps = ['deployment']