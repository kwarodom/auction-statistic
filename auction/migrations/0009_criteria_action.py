# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0008_remove_product_updated_on'),
    ]

    operations = [
        migrations.AddField(
            model_name='criteria',
            name='action',
            field=models.BooleanField(default=False),
        ),
    ]
