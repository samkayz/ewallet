# Generated by Django 2.2 on 2019-10-10 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0006_merchant'),
    ]

    operations = [
        migrations.CreateModel(
            name='MerchantPayment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bus_owner_username', models.CharField(max_length=100)),
                ('payee', models.CharField(max_length=100)),
                ('amount', models.CharField(max_length=200)),
            ],
        ),
    ]
