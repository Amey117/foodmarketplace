# Generated by Django 5.0.4 on 2024-04-20 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0003_alter_vendor_is_approved_alter_vendor_is_rejected'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendor',
            name='is_rejected',
            field=models.BooleanField(null=True),
        ),
    ]
