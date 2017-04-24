# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0010_auto_20161220_1120'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statistic',
            name='user',
            field=models.ForeignKey(null=True, to='auction.User'),
        ),
    ]
