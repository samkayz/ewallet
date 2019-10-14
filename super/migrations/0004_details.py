# Generated by Django 2.2 on 2019-10-13 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('super', '0003_auto_20191012_2139'),
    ]

    operations = [
        migrations.CreateModel(
            name='Details',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=200)),
                ('email', models.CharField(max_length=50)),
                ('phone_no', models.CharField(max_length=20)),
                ('fax', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'details',
            },
        ),
    ]
