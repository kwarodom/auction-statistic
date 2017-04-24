# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import auction.fields


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0023_auto_20161227_1626'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statistic',
            name='bid_type',
            field=auction.fields.PositiveTinyIntegerField(choices=[(1, 'Single Bid'), (2, 'Auto Bid'), (3, 'SMS Bid')], blank=True, null=True),
        ),
    ]
