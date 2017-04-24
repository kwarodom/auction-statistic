# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0007_product_updated_on'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='updated_on',
        ),
    ]
