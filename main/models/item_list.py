from django.db import models

from main.models.on_sale import OnSale
from main.models.category import Category
from main.models.company import Company
from main.models.receipt import Receipt
from main.models.item import Item
from main.models.tax import Tax


class ItemList(models.Model):
    id = models.AutoField(primary_key=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='item_list')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    is_taxed = models.ForeignKey(Tax, on_delete=models.SET_NULL, related_name='item_list', null=True)
    is_on_sale = models.ForeignKey(OnSale, on_delete=models.SET_NULL, related_name='item_list', null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='item_list', null=True)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, related_name='item_list', null=True)
    remarks = models.TextField(max_length=500)
    receipt = models.ForeignKey(Receipt, on_delete=models.SET_NULL, related_name='item_list', null=True)
    shopping_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    