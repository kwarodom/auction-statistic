# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('item_id', models.AutoField(serialize=False, primary_key=True)),
                ('item_name', models.CharField(blank=True, max_length=1024, null=True)),
                ('item_image', models.ImageField(blank=True, null=True, upload_to='item/')),
                ('item_price', models.FloatField(blank=True, null=True)),
                ('item_c_price', models.FloatField(blank=True, null=True)),
                ('item_discounted', models.FloatField(blank=True, null=True)),
                ('item_winner', models.CharField(blank=True, max_length=256, null=True)),
                ('item_bids', models.PositiveIntegerField(blank=True, null=True)),
                ('item_terminated_on', models.DateTimeField(blank=True, null=True)),
                # ('enable_fetch_statistic', models.BooleanField(default=False)),
            ],
        ),
    ]
