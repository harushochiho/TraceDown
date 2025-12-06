from django.db import models


class Company(models.Model):
    id = models.AutoField(primary_key=True)
    company_name = models.CharField(max_length=255)