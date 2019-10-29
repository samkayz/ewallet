from django.db import models


class Resolution(models.Model):
    ticket_id = models.CharField(max_length=50)
    subject = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    content = models.CharField(max_length=500)
    date = models.DateField(auto_now=True)

    class Meta:
        db_table = "resolution"


class Settings(models.Model):
    about_us = models.CharField(max_length=1000)
    address = models.CharField(max_length=1000)
    phone_no = models.CharField(max_length=1000)
    email = models.EmailField(max_length=100)
    paystack_api = models.CharField(max_length=200)

    class Meta:
        db_table = "settings"


class Details(models.Model):
    address = models.CharField(max_length=200)
    email = models.CharField(max_length=50)
    phone_no = models.CharField(max_length=20)
    fax = models.CharField(max_length=20)

    class Meta:
        db_table = "details"


