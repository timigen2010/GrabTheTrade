# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-21 16:37
from __future__ import unicode_literals

from django.db import migrations
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('gtt', '0004_auto_20170520_1605'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='country',
            managers=[
                ('country', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='resource',
            managers=[
                ('resource', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='template',
            managers=[
                ('template', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='tradeinfo',
            managers=[
                ('info', django.db.models.manager.Manager()),
            ],
        ),
        migrations.RenameField(
            model_name='analyzedtradeinfo',
            old_name='country_id',
            new_name='country',
        ),
        migrations.RenameField(
            model_name='analyzedtradeinfo',
            old_name='direction_type_id',
            new_name='direction_type',
        ),
        migrations.RenameField(
            model_name='analyzedtradeinfo',
            old_name='partner_id',
            new_name='partner',
        ),
        migrations.RenameField(
            model_name='prediction',
            old_name='analyzed_trade_info_id',
            new_name='analyzed_trade_info',
        ),
        migrations.RenameField(
            model_name='resource',
            old_name='template_id',
            new_name='template',
        ),
        migrations.RenameField(
            model_name='statistic',
            old_name='country_id',
            new_name='country',
        ),
        migrations.RenameField(
            model_name='statistic',
            old_name='partner_id',
            new_name='partner',
        ),
        migrations.RenameField(
            model_name='tradeinfo',
            old_name='country_id',
            new_name='country',
        ),
        migrations.RenameField(
            model_name='tradeinfo',
            old_name='direction_type_id',
            new_name='direction_type',
        ),
        migrations.RenameField(
            model_name='tradeinfo',
            old_name='partner_id',
            new_name='partner',
        ),
        migrations.RenameField(
            model_name='tradeinfo',
            old_name='resource_id',
            new_name='resource',
        ),
    ]