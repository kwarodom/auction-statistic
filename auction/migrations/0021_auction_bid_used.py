# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0020_auto_20161227_1310'),
    ]

    operations = [
        migrations.AddField(
            model_name='auction',
            name='bid_used',
            field=models.PositiveIntegerField(null=True, blank=True),
        ),
    ]
