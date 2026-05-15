import datetime

from django.db import models


class Receipt(models.Model):
    id = models.AutoField(primary_key=True)
    picture = models.ImageField(upload_to='receipts/', blank=True, null=True)
    shopping_date = models.DateField(default=datetime.date.today)
    name = models.TextField(max_length=255, null=False, blank=False, unique=False, default=datetime.date.today().isoformat())