# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-18 20:17
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('noshpit', '0003_auto_20170713_1656'),
    ]

    operations = [
        migrations.CreateModel(
            name='PitPhoto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='noshpit.Photo')),
                ('pit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='noshpit.Pit')),
            ],
        ),
    ]