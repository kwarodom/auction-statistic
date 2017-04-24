# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import auction.models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0022_auto_20161227_1619'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='item_id',
            field=models.PositiveSmallIntegerField(primary_key=True, default=auction.models.Product._id, serialize=False),
        ),
    ]
