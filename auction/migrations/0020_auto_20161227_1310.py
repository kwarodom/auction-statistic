# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0019_auto_20161227_1238'),
    ]

    operations = [
        migrations.CreateModel(
            name='History',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('json', jsonfield.fields.JSONField()),
                ('fetched_on', models.DateTimeField(auto_now_add=True)),
                ('item', models.ForeignKey(to='auction.Product')),
            ],
        ),
        migrations.AlterField(
            model_name='action',
            name='auction_json',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='auction.Criteria'),
        ),
        migrations.AlterField(
            model_name='action',
            name='history_json',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='auction.History'),
        ),
    ]
