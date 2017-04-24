# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0002_statistic'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='enable_fetch_statistic',
            field=models.BooleanField(default=False),
        ),
    ]
