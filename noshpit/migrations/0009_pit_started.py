# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-24 20:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('noshpit', '0008_user_finished'),
    ]

    operations = [
        migrations.AddField(
            model_name='pit',
            name='started',
            field=models.BooleanField(default=False),
        ),
    ]