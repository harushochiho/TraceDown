import datetime

from django.db import models


class Receipt(models.Model):
    id = models.AutoField(primary_key=True)
    picture = models.ImageField(upload_to='receipts/', blank=True, null=True)
    shopping_date = models.DateTimeField(auto_now_add=True)
    name = models.TextField(max_length=255, null=False, blank=False, unique=False, default=datetime.date.today().isoformat())
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    taxes = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)