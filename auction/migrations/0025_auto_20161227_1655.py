# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0024_auto_20161227_1634'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountsetting',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
