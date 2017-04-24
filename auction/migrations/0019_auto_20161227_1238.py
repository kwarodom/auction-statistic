# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0018_auto_20161225_1150'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountSetting',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(null=True, max_length=256, blank=True)),
                ('php_session_id', models.CharField(null=True, max_length=32, blank=True)),
                ('bids', models.IntegerField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('action', models.PositiveSmallIntegerField(null=True, choices=[(1, 'Single Bid'), (2, 'Auto Bid'), (3, 'SMS Bid'), (10, 'Cancel Auto Bid'), (20, 'Terminate Auction')], blank=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('auction_json', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='auction.Statistic', null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Auction',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('enable_smart_bid', models.BooleanField(default=False)),
                ('status', models.PositiveSmallIntegerField(null=True, choices=[(0, 'DISABLED'), (1, 'ACTIVE'), (2, 'AUTO'), (10, 'CANCELED'), (20, 'TERMINATED'), (20, 'WIN'), (20, 'LOST')], blank=True)),
                ('price_min', models.FloatField(null=True, blank=True)),
                ('price_max', models.FloatField(null=True, blank=True)),
                ('bid_limit', models.PositiveIntegerField(null=True, blank=True)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='auction.Product', null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('json', jsonfield.fields.JSONField()),
                ('fetched_on', models.DateTimeField(auto_now_add=True)),
                ('item', models.ForeignKey(to='auction.Product')),
            ],
        ),
        migrations.RemoveField(
            model_name='criteria',
            name='action',
        ),
        migrations.AddField(
            model_name='action',
            name='history_json',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='auction.Criteria', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='action',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='auction.Auction', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='action',
            name='result_json',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='auction.Result', null=True, blank=True),
        ),
    ]
