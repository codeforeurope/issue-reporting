# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-05-17 13:29
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service_code', models.CharField(db_index=True, max_length=64)),
                ('identifier', models.CharField(max_length=64, unique=True)),
                ('description', models.TextField()),
                ('status', models.CharField(blank=True, choices=[('open', 'open'), ('closed', 'closed')], db_index=True, default='open', max_length=32)),
                ('status_notes', models.TextField(blank=True)),
                ('agency_responsible', models.CharField(blank=True, max_length=140)),
                ('service_notice', models.TextField(blank=True)),
                ('requested_datetime', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_datetime', models.DateTimeField(default=django.utils.timezone.now)),
                ('expected_datetime', models.DateTimeField(null=True)),
                ('address', models.TextField(blank=True)),
                ('zipcode', models.CharField(blank=True, db_index=True, max_length=10)),
                ('media_url', models.URLField(blank=True)),
                ('submitter_email', models.EmailField(blank=True, max_length=254)),
                ('submitter_first_name', models.CharField(blank=True, max_length=140)),
                ('submitter_last_name', models.CharField(blank=True, max_length=140)),
                ('submitter_phone', models.CharField(blank=True, max_length=140)),
                ('location', django.contrib.gis.db.models.fields.PointField(db_index=True, blank=True, null=True, srid=4326)),
            ],
        ),
        migrations.CreateModel(
            name='Jurisdiction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(max_length=64, unique=True)),
                ('name', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service_code', models.CharField(max_length=120, unique=True)),
                ('service_name', models.CharField(max_length=120)),
                ('description', models.TextField(blank=True)),
                ('metadata', models.BooleanField(default=False)),
                ('type', models.CharField(choices=[('realtime', 'Realtime'), ('batch', 'Batch'), ('blackbox', 'Black Box')], default='realtime', max_length=140)),
                ('keywords', models.TextField(blank=True)),
                ('group', models.CharField(blank=True, default='', max_length=140)),
                ('jurisdictions', models.ManyToManyField(related_name='services', to='issues.Jurisdiction')),
            ],
        ),
        migrations.AddField(
            model_name='issue',
            name='jurisdiction',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='issues.Jurisdiction'),
        ),
        migrations.AddField(
            model_name='issue',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='issues.Service'),
        ),
    ]
