# Generated by Django 5.0.4 on 2024-07-22 17:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('initiated', 'Initiated'), ('accepted', 'Accepted'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='New', max_length=15),
        ),
        migrations.AlterField(
            model_name='payment',
            name='payment_method',
            field=models.CharField(max_length=100),
        ),
    ]
