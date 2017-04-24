# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0013_statistic_bid_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='item_winner',
        ),
        migrations.AddField(
            model_name='product',
            name='user',
            field=models.ForeignKey(null=True, to='auction.User'),
        ),
    ]
