from decimal import Decimal

from django.core.files.storage import default_storage
from django.shortcuts import render

from main.models import Receipt, Item, ItemList, Company, Category, Tax, OnSale


# Create your views here.
def create_item(request):
    return render(request, "create_item.html")

def submit_item(request):
    # Create a new object and save to the table "receipt"
    image_file = request.FILES['picture']
    filename = default_storage.save(f'receipts/{image_file.name}', image_file)
    receipt_obj = Receipt(picture=filename, name=request.POST["receipt"])
    receipt_obj.save()

    # Check if the item name exists
    # True: use existing item name
    # False: create a new one and save to the table "item"
    item_obj, item_exists = Item.objects.get_or_create(name=request.POST["item"])
    if not item_exists:
        item_obj.save()

    # Check if the company name exists
    # True: use existing company name
    # False: create a new one and save to the table "company"
    company_obj, company_exists = Company.objects.get_or_create(company_name=request.POST["company"])
    if not company_exists:
        company_obj.save()

    # Check if the category name exists
    # True: use existing category name
    # False: create a new one and save to the table "category"
    category_obj, category_exists = Category.objects.get_or_create(name=request.POST["category"])
    if not category_exists:
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