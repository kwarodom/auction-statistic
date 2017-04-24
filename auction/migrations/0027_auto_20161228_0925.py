# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0026_auction_auto_bid_activated'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='action',
            name='item',
        ),
        migrations.RemoveField(
            model_name='auction',
            name='id',
        ),
        migrations.AlterField(
            model_name='auction',
            name='item',
            field=models.OneToOneField(default=11051, to='auction.Product', serialize=False, primary_key=True),
            preserve_default=False,
        ),
    ]
