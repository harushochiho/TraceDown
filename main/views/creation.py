import base64
import json
from decimal import Decimal
from io import BytesIO
from os.path import splitext
from unittest import result
from zoneinfo import ZoneInfo

from django.core.files.storage import default_storage
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.utils import timezone

from main.models import Receipt, Item, ItemList, Company, Category, Tax, OnSale
from main.services import image_recognition
from main.utils import ImageProcessing


# Create your views here.
def create_item(request):
    return render(request, "create_item.html")


def submit_item(request):
    # Create a new object and save to the table "receipt"
    receipt_obj, _ = Receipt.objects.get_or_create(name=request.POST["receipt"])
    if request.FILES:
        image_file = request.FILES['picture']
        filename = default_storage.save(f'receipts/{image_file.name}', image_file)
        receipt_obj.picture = filename
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

    is_taxed = Tax.objects.get(is_taxed='tax' in request.POST if 1 else 0)
    is_on_sale = OnSale.objects.get(is_on_sale='onsale' in request.POST if 1 else 0)

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


def image_upload(request):
    return render(request, "image_upload.html")


def image_recognition_req(request):
    print(request.FILES)
    file = request.FILES.get('picture')
    if not file:
        return HttpResponseBadRequest("No file uploaded.")

    # Read image from the uploaded file
    receipt_img = file.read()

    # Create an instance of ImageProcessing and process the image
    image_processing = ImageProcessing()
    image_processing.process_image(BytesIO(receipt_img))

    # timezone.activate(ZoneInfo("America/Toronto"))
    # folder_name = f"{splitext(file.name)[0]}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
    # default_storage.save(f'receipts/{folder_name}/test-origin_{file.name}', image_processing.get_origin_image_bytes())
    # default_storage.save(f'receipts/{folder_name}/test-transformed_{file.name}', image_processing.get_transformed_image_bytes())

    image_encoded = base64.b64encode(image_processing.get_transformed_image_bytes().getvalue()).decode("utf-8")
    
    try:
        ai_res = image_recognition(image_encoded)
    
        data = json.loads(ai_res)
    
        save_receipt_from_json(data, {'origin': image_processing.get_origin_image_bytes(),
                                  'transformed': image_processing.get_transformed_image_bytes(), 'name': file.name})
    
        return redirect('retrieval')
    except Exception as e:
        return JsonResponse({'error': str(e)})


def save_receipt_from_json(data, images: {'origin': BytesIO, 'transformed': BytesIO, 'name': str}):
    # Create a new object and save to the table "receipt"
    receipt_obj, _ = Receipt.objects.get_or_create(name=data['CompanyName'], shopping_date=data['Date'])
    if images:
        timezone.activate(ZoneInfo("America/Toronto"))
        folder_name = f"{splitext(images['name'])[0]}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        filename = default_storage.save(f'receipts/{folder_name}/origin_{images['name']}', images['origin'])
        default_storage.save(f'receipts/{folder_name}/transformed_{images['name']}', images['transformed'])
        receipt_obj.picture = filename
    receipt_obj.save()

    # Check if the company name exists
    # True: use existing company name
    # False: create a new one and save to the table "company"
    company_obj, _ = Company.objects.get_or_create(company_name=data['CompanyName'])

    for item in data['items']:
        # Check if the item name exists
        # True: use existing item name
        # False: create a new one and save to the table "item"
        item_obj, _ = Item.objects.get_or_create(name=item['name'])

        # Check if the category name exists
        # True: use existing category name
        # False: create a new one and save to the table "category"
        category_obj, _ = Category.objects.get_or_create(name=item['Category'])

        is_taxed = Tax.objects.get(is_taxed=item['Taxable'])
        is_on_sale = OnSale.objects.get(is_on_sale=item['OnSale'])

        item_list = ItemList(
            item=item_obj,
            price=Decimal(item['totalPrice']),
            quantity=Decimal(item['quantity']),
            category=category_obj,
            company=company_obj,
            is_taxed=is_taxed,
            is_on_sale=is_on_sale,
            remarks='',
            receipt=receipt_obj,
        )
        item_list.save()
