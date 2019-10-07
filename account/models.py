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


class Ticket(models.Model):
    subject = models.CharField(max_length=500)
    category = models.CharField(max_length=100)
    owner = models.CharField(max_length=100)
    content = models.CharField(max_length=1000)
    priority = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    ticket_id = models.CharField(max_length=10)
    date_created = models.DateField(auto_now=True)
    date_action = models.CharField(max_length=100)


class Merchant(models.Model):
    bus_owner_username = models.CharField(max_length=100)
    bus_name = models.CharField(max_length=200)
    bus_address = models.CharField(max_length=200)
    bus_email = models.CharField(max_length=100)
    bus_no = models.CharField(max_length=20)
    bus_website = models.CharField(max_length=200)
    api_test_key = models.CharField(max_length=200)
    api_live_key = models.CharField(max_length=200)
