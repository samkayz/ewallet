# Generated by Django 2.2.7 on 2019-11-25 12:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0022_banks'),
    ]

    operations = [
        migrations.CreateModel(
            name='VirtualCard',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card_user', models.CharField(max_length=100)),
                ('card_no', models.CharField(max_length=100)),
                ('pin', models.CharField(max_length=10)),
                ('card_bal', models.CharField(max_length=1000)),
            ],
            options={
                'db_table': 'virtual_card',
            },
        ),
    ]
