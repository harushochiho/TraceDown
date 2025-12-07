from decimal import Decimal

from django.shortcuts import render

from main.models import Receipt, Item, ItemList, Company, Category, Tax, OnSale


# Create your views here.
def create_item(request):
    return render(request, "create_item.html")

def submit_item(request):
    print(request.POST)
    receipt_obj = Receipt(picture='')
    receipt_obj.save()
    print(receipt_obj)
    item_obj, _ = Item.objects.get_or_create(name=request.POST["item"])
    print(item_obj)
    item_obj.save()
    company_obj, _ = Company.objects.get_or_create(company_name=request.POST["company"])
    company_obj.save()
    category_obj, _ = Category.objects.get_or_create(name=request.POST["category"])
    category_obj.save()
    is_taxed = Tax.objects.get(id='tax' in request.POST if 0 else 1)
    is_on_sale = OnSale.objects.get(id='onsale' in request.POST if 0 else 1)
    item_list = ItemList(
        item=item_obj,
        price=Decimal(request.POST["price"]),
        quantity=Decimal(request.POST["quantity"]),
        category=category_obj,
        company=company_obj,
        is_taxed=is_taxed,
        is_on_sale=is_on_sale,
        remarks=request.POST["remarks"],
        receipt=receipt_obj,
    )
    item_list.save()
    return render(request, "create_item.html")