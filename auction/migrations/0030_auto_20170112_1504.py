# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0029_auto_20161228_0941'),
    ]

    operations = [
        migrations.AddField(
            model_name='accountsetting',
            name='password',
            field=models.CharField(max_length=255, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='accountsetting',
            name='username',
            field=models.CharField(max_length=255, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='action',
            name='action',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Single Bid'), (2, 'Auto Bid'), (3, 'SMS Bid'), (5, 'Single Recovery'), (10, 'Cancel Auto Bid'), (20, 'Terminate Auction')], blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='auction',
            name='bid_used',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
    ]
