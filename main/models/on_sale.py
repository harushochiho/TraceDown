from django.db import models


class OnSale(models.Model):
    id = models.AutoField(primary_key=True)
    is_on_sale = models.BooleanField()
    desc = models.TextField(max_length=5)