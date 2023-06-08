# Generated by Django 2.2.4 on 2019-10-04 07:07

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pegasus_examples', '0002_employee'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pegasus_payments', to=settings.AUTH_USER_MODEL),
        ),
    ]