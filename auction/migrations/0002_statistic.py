# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Statistic',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('price', models.FloatField()),
                ('user', models.CharField(max_length=256)),
                ('fetched_on', models.DateTimeField(auto_now_add=True)),
                ('item', models.ForeignKey(to='auction.Product')),
            ],
        ),
    ]
