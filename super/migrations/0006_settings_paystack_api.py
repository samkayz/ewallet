# Generated by Django 2.2 on 2019-10-25 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('super', '0005_auto_20191017_1915'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='paystack_api',
            field=models.CharField(default=1, max_length=200),
            preserve_default=False,
        ),
    ]
