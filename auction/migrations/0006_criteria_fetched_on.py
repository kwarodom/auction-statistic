# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0005_criteria'),
    ]

    operations = [
        migrations.AddField(
            model_name='criteria',
            name='fetched_on',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2016, 12, 20, 6, 4, 22, 870108)),
            preserve_default=False,
        ),
    ]
