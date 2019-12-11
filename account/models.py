from django.db import models


class Account(models.Model):
    username = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_no = models.CharField(max_length=20)
    customer_id = models.CharField(max_length=10)
    bal = models.CharField(max_length=200)
    status = models.CharField(max_length=100)

    class Meta:
        db_table = "account"


class Transactions(models.Model):
    sender = models.CharField(max_length=50)
    receiver = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    amount = models.CharField(max_length=200)
    ref_no = models.CharField(max_length=40)
    date = models.DateField(auto_now=True)

    class Meta:
        db_table = "transactions"


class Voucher(models.Model):
    v_creator = models.CharField(max_length=100)
    v_code = models.CharField(max_length=20)
    v_amount = models.CharField(max_length=200)
    ref_no = models.CharField(max_length=100)
    v_status = models.CharField(max_length=10)
    v_loader = models.CharField(max_length=100)
    v_date_load = models.CharField(max_length=100)
    v_date = models.DateField(auto_now=True)

    class Meta:
        db_table = "voucher"


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

    class Meta:
        db_table = "ticket"


class Merchant(models.Model):
    bus_owner_username = models.CharField(max_length=100)
    bus_name = models.CharField(max_length=200)
    bus_address = models.CharField(max_length=200)
    bus_email = models.CharField(max_length=100)
    bus_no = models.CharField(max_length=20)
    bus_website = models.CharField(max_length=200)
    api_test_key = models.CharField(max_length=200)
    api_live_key = models.CharField(max_length=200)
    bus_logo = models.FileField(upload_to='media')
    int_mode = models.CharField(max_length=100)
    w_p_charges = models.CharField(max_length=100)

    class Meta:
        db_table = "merchant"


class MerchantPayment(models.Model):
    bus_owner_username = models.CharField(max_length=100)
    payee = models.CharField(max_length=100)
    amount = models.CharField(max_length=200)

    class Meta:
        db_table = "merchantPayment"


class Bank(models.Model):
    username = models.CharField(max_length=100)
    account_name = models.CharField(max_length=100)
    account_no = models.CharField(max_length=100)
    bank_name = models.CharField(max_length=20)

    class Meta:
        db_table = "bank"


class Withdraw(models.Model):
    username = models.CharField(max_length=100)
    amount = models.CharField(max_length=100)
    acct_name = models.CharField(max_length=200)
    acct_no = models.CharField(max_length=200)
    bank_name = models.CharField(max_length=100)
    ref_no = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    date = models.DateField(auto_now=True)

    class Meta:
        db_table = "withdraw"


class Invoice(models.Model):
    sender = models.CharField(max_length=100)
    receiver = models.CharField(max_length=100)
    amount = models.CharField(max_length=100)
    content = models.CharField(max_length=500)
    date = models.DateField(auto_now=True)
    status = models.CharField(max_length=10)
    date_paid = models.CharField(max_length=100)
    action = models.CharField(max_length=50)

    class Meta:
        db_table = "invoice"


class Subscription(models.Model):
    email = models.CharField(max_length=200)
    date_reg = models.DateField(auto_now=True)

    class Meta:
        db_table = "subscription"


class Banks(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100)

    class Meta:
        db_table = "banks"


class VirtualCard(models.Model):
    card_user = models.CharField(max_length=100)
    card_no = models.CharField(max_length=100)
    pin = models.CharField(max_length=10)
    card_bal = models.CharField(max_length=1000)

    class Meta:
        db_table = "virtual_card"


class Customer(models.Model):
    merchant_id = models.IntegerField()
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone_no = models.CharField(max_length=100)

    class Meta:
        db_table = 'customer'


class Staff(models.Model):
    merchant_id = models.IntegerField()
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone_no = models.CharField(max_length=100)
    amount = models.FloatField()

    class Meta:
        db_table = 'staff'


