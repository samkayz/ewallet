# Generated by Django 2.2.7 on 2019-11-15 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0019_subscription'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='date_reg',
            field=models.DateField(auto_now=True),
        ),
    ]