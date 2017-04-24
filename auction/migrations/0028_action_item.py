# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0027_auto_20161228_0925'),
    ]

    operations = [
        migrations.AddField(
            model_name='action',
            name='item',
            field=models.ForeignKey(blank=True, to='auction.Auction', on_delete=django.db.models.deletion.SET_NULL, null=True),
        ),
    ]
