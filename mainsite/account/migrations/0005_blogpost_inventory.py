# Generated by Django 3.0.4 on 2020-04-20 06:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_auto_20200420_0429'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogpost',
            name='inventory',
            field=models.DecimalField(decimal_places=2, default='0', max_digits=7),
        ),
    ]
