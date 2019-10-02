from django.db import models
from django.contrib.auth.models import User


class Account(models.Model):
    username = models.CharField(max_length=100)
    phone_no = models.CharField(max_length=20)
    customer_id = models.CharField(max_length=10)
    bal = models.CharField(max_length=200)
