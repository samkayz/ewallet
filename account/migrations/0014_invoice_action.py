# Generated by Django 2.2 on 2019-10-20 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0013_invoice'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='action',
            field=models.CharField(default=1, max_length=10),
            preserve_default=False,
        ),
    ]
