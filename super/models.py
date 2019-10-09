from django.db import models


class Resolution(models.Model):
    ticket_id = models.CharField(max_length=50)
    subject = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    content = models.CharField(max_length=500)
    date = models.DateField(auto_now=True)


