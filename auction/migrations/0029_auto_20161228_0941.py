# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0028_action_item'),
    ]

    operations = [
        migrations.RenameField(
            model_name='action',
            old_name='item',
            new_name='auction',
        ),
        migrations.RenameField(
            model_name='action',
            old_name='auction_json',
            new_name='criteria_json',
        ),
    ]
