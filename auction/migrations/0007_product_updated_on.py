# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0006_criteria_fetched_on'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='updated_on',
            field=models.DateTimeField(default=datetime.datetime(2016, 12, 20, 6, 5, 33, 737047), auto_now=True),
            preserve_default=False,
        ),
    ]
