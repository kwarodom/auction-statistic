# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0015_auto_20161220_1232'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='enable_smart_bid',
            field=models.BooleanField(default=False),
        ),
    ]
