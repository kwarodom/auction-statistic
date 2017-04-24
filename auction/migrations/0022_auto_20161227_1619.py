# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import auction.models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0021_auction_bid_used'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='id',
            field=models.PositiveSmallIntegerField(default=auction.models.User._id, primary_key=True, serialize=False),
        ),
    ]
