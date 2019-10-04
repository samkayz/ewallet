from django.db import models


class Account(models.Model):
    username = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_no = models.CharField(max_length=20)
    customer_id = models.CharField(max_length=10)
    bal = models.CharField(max_length=200)


class Transactions(models.Model):
    sender = models.CharField(max_length=50)
    receiver = models.CharField(max_length=50)
    amount = models.CharField(max_length=200)
    ref_no = models.CharField(max_length=40)
    date = models.DateField(auto_now=True)


class Voucher(models.Model):
    v_creator = models.CharField(max_length=100)
    v_code = models.CharField(max_length=20)
    v_amount = models.CharField(max_length=200)
    ref_no = models.CharField(max_length=100)
    v_status = models.CharField(max_length=10)
    v_loader = models.CharField(max_length=100)
    v_date_load = models.CharField(max_length=100)
    v_date = models.DateField(auto_now=True)
