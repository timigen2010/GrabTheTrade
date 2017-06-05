# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-03 09:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AnalyzedTradeInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField()),
                ('value', models.FloatField()),
            ],
            managers=[
                ('info', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=255)),
                ('rus', models.CharField(max_length=255, null=True)),
            ],
            managers=[
                ('country', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='Data',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='DirectionType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Prediction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.FloatField()),
                ('analyzed_trade_info', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gtt.AnalyzedTradeInfo')),
            ],
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('url', models.TextField()),
            ],
            managers=[
                ('resource', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='Statistic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField()),
                ('index', models.FloatField()),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='statistic_country', to='gtt.Country')),
                ('partner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='statistic_partner', to='gtt.Country')),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('body', models.TextField()),
                ('date_start', models.DateTimeField()),
                ('date_end', models.DateTimeField(null=True)),
                ('resource', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gtt.Resource')),
            ],
            managers=[
                ('task', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.TextField()),
            ],
            managers=[
                ('template', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='TradeInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField()),
                ('value', models.FloatField()),
                ('used', models.BooleanField(default=0)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trade_country', to='gtt.Country')),
                ('direction_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gtt.DirectionType')),
                ('partner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trade_partner', to='gtt.Country')),
                ('resource', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gtt.Resource')),
            ],
            managers=[
                ('info', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AddField(
            model_name='resource',
            name='template',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gtt.Template'),
        ),
        migrations.AddField(
            model_name='analyzedtradeinfo',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='analyzed_trade_country', to='gtt.Country'),
        ),
        migrations.AddField(
            model_name='analyzedtradeinfo',
            name='direction_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gtt.DirectionType'),
        ),
        migrations.AddField(
            model_name='analyzedtradeinfo',
            name='partner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='analyzed_trade_partner', to='gtt.Country'),
        ),
        migrations.AlterUniqueTogether(
            name='tradeinfo',
            unique_together=set([('resource', 'country', 'partner', 'direction_type', 'year')]),
        ),
        migrations.AlterUniqueTogether(
            name='statistic',
            unique_together=set([('country', 'partner', 'year')]),
        ),
        migrations.AlterUniqueTogether(
            name='analyzedtradeinfo',
            unique_together=set([('country', 'partner', 'direction_type', 'year')]),
        ),
    ]
