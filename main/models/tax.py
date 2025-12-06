from django.db import models


class Tax(models.Model):
    id = models.AutoField(primary_key=True)
    is_taxed = models.BooleanField()
    desc = models.TextField(max_length=5)