# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-20 11:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gtt', '0002_auto_20170520_1408'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tradeinfo',
            name='year',
            field=models.IntegerField(),
        ),
    ]