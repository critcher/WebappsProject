# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-12 16:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('framework', '0009_auto_20160408_2238'),
    ]

    operations = [
        migrations.AddField(
            model_name='calendaruser',
            name='isDev',
            field=models.BooleanField(default=False),
        ),
    ]