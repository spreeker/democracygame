# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models
from django.template.defaultfilters import slugify
import re

class Migration(DataMigration):

    def forwards(self, orm):
        "create slugfields from issue titels"
        for issue in orm.Issue.objects.all():
            slug = self._unique_slugify(issue,issue.title) 
            issue.save()

    def backwards(self, orm):
        "Write your backwards methods here."

    def _unique_slugify(self, instance, value, slug_field_name='slug', queryset=None,
                        slug_separator='-'):
        """
        Calculates a unique slug of ``value`` for an instance.

        :param slug_field_name: Should be a string matching the name of the field to
            store the slug in (and the field to check against for uniqueness).

        :param queryset: usually doesn't need to be explicitly provided - it'll
            default to using the ``.all()`` queryset from the model's default
            manager.
        
        """
        slug_field = instance._meta.get_field(slug_field_name)
        
        slug_len = slug_field.max_length

        # Sort out the initial slug. Chop its length down if we need to.
        slug = slugify(value)
        if slug_len:
            slug = slug[:slug_len]
        slug = self._slug_strip(slug, slug_separator)
        original_slug = slug

        # Create a queryset, excluding the current instance.
        if queryset is None:
            queryset = instance.__class__._default_manager.all()
            if instance.pk:
                queryset = queryset.exclude(pk=instance.pk)

        # Find a unique slug. If one matches, at '-2' to the end and try again
        # (then '-3', etc).
        next = 2
        while not slug or queryset.filter(**{slug_field_name: slug}):
            slug = original_slug
            end = '-%s' % next
            if slug_len and len(slug) + len(end) > slug_len:
                slug = slug[:slug_len-len(end)]
                slug = self._slug_strip(slug, slug_separator)
            slug = '%s%s' % (slug, end)
            next += 1

        setattr(instance, slug_field.attname, slug)
        return slug

    def _slug_strip(self, value, separator=None):
        """
        Cleans up a slug by removing slug separator characters that occur at the
        beginning or end of a slug.

        If an alternate separator is used, it will also replace any instances of the
        default '-' separator with the new separator.
        
        """
        if separator == '-' or not separator:
            re_sep = '-'
        else:
            re_sep = '(?:-|%s)' % re.escape(separator)
            value = re.sub('%s+' % re_sep, separator, value)
        return re.sub(r'^%s+|%s+$' % (re_sep, re_sep), '', value)


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'issue.issue': {
            'Meta': {'object_name': 'Issue'},
            'body': ('django.db.models.fields.TextField', [], {'max_length': '2000'}),
            'hotness': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_draft': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'offensiveness': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'score': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '80', 'null': 'True', 'db_index': 'True'}),
            'source_type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'time_stamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2010, 9, 16, 14, 22, 35, 461061)'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'votes': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['issue']
