# Generated by Django 2.2.7 on 2019-11-16 10:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('super', '0007_emails'),
    ]

    operations = [
        migrations.CreateModel(
            name='Commission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pay_me', models.CharField(max_length=10)),
                ('invoice', models.CharField(max_length=10)),
                ('transfer', models.CharField(max_length=10)),
                ('deposit', models.CharField(max_length=10)),
                ('merchant', models.CharField(max_length=10)),
            ],
            options={
                'db_table': 'commission',
            },
        ),
    ]