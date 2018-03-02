# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-03-02 19:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('schedule', '0001_initial'),
        ('acquisitions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='acquisition',
            name='schedule_entry',
            field=models.ForeignKey(help_text=b'The schedule entry relative to the acquisition', on_delete=django.db.models.deletion.PROTECT, related_name='acquisitions', to='schedule.ScheduleEntry'),
        ),
        migrations.AlterUniqueTogether(
            name='acquisition',
            unique_together=set([('schedule_entry', 'task_id')]),
        ),
    ]
