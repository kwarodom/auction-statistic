# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0025_auto_20161227_1655'),
    ]

    operations = [
        migrations.AddField(
            model_name='auction',
            name='auto_bid_activated',
            field=models.BooleanField(default=False),
        ),
    ]
