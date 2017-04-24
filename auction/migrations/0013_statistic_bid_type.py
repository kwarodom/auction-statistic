# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0012_auction_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='statistic',
            name='bid_type',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Single Bid'), (2, 'Auto Bid'), (3, 'SMS Bid')], null=True),
        ),
    ]
