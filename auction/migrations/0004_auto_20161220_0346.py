# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0003_product_enable_fetch_statistic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='enable_fetch_statistic',
            field=models.BooleanField(default=True),
        ),
    ]
