# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0004_auto_20161220_0346'),
    ]

    operations = [
        migrations.CreateModel(
            name='Criteria',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('json', jsonfield.fields.JSONField()),
                ('item', models.ForeignKey(to='auction.Product')),
            ],
        ),
    ]
