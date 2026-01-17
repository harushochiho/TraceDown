from pprint import pprint

from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from main.models import ItemList, Item, Receipt, Category, Company, Tax, OnSale


@require_http_methods(["POST"])
def update_item(request, item_id):
    """
    Handle POST request to update an item from the edit modal.
    
    Expected POST data:
    - item_name: str
    - price: decimal
    - quantity: decimal
    - tax: boolean (checkbox)
    - onsale: boolean (checkbox)
    - category: str
    - company: str
    - remarks: str
    - shopping_date: date
    - picture: file (optional)
    """
    try:
        # Get the ItemList object
        item_list = get_object_or_404(ItemList, id=item_id)
        
        # Display received POST data
        print("\n" + "="*50)
        print(f"UPDATE REQUEST RECEIVED FOR ITEM ID: {item_id}")
        print("="*50)
        print("POST DATA:")
        pprint(dict(request.POST))
        print("\nFILES DATA:")
        pprint(dict(request.FILES))
        print("="*50 + "\n")
        
        # Get or create Item
        item_name = request.POST.get('item_name', '').strip()
        print(f"Item Name: {item_name}")
        if item_name:
            item, _ = Item.objects.get_or_create(name=item_name)
            item_list.item = item
        
        # Update basic item fields
        price = request.POST.get('price', item_list.price)
        quantity = request.POST.get('quantity', item_list.quantity)
        remarks = request.POST.get('remarks', '')
        item_list.price = price
        item_list.quantity = quantity
        item_list.remarks = remarks
        print(f"Price: {price}, Quantity: {quantity}, Remarks: {remarks}")
        
        # Handle Tax
        tax_checkbox = request.POST.get('tax') == 'on' or request.POST.get('tax') == 'true'
        print(f"Tax Checkbox: {tax_checkbox}")
        if tax_checkbox:
            tax, _ = Tax.objects.get_or_create(is_taxed=True, defaults={'desc': 'Y'})
            item_list.is_taxed = tax
        else:
            tax, _ = Tax.objects.get_or_create(is_taxed=False, defaults={'desc': 'N'})
            item_list.is_taxed = tax
        
        # Handle On Sale
        on_sale_checkbox = request.POST.get('onsale') == 'on' or request.POST.get('onsale') == 'true'
        print(f"On Sale Checkbox: {on_sale_checkbox}")
        if on_sale_checkbox:
            on_sale, _ = OnSale.objects.get_or_create(is_on_sale=True, defaults={'desc': 'Y'})
            item_list.is_on_sale = on_sale
        else:
            on_sale, _ = OnSale.objects.get_or_create(is_on_sale=False, defaults={'desc': 'N'})
            item_list.is_on_sale = on_sale
        
        # Handle Category
        category_name = request.POST.get('category', '').strip()
        print(f"Category: {category_name}")
        if category_name:
            category, _ = Category.objects.get_or_create(name=category_name)
            item_list.category = category
        else:
            item_list.category = None
        
        # Handle Company
        company_name = request.POST.get('company', '').strip()
        print(f"Company: {company_name}")
        if company_name:
            company, _ = Company.objects.get_or_create(company_name=company_name)
            item_list.company = company
        else:
            item_list.company = None
        
        # Handle Receipt - update shopping date and picture if provided
        shopping_date = request.POST.get('shopping_date')
        print(f"Shopping Date: {shopping_date}")
        receipt = item_list.receipt
        if receipt:
            if shopping_date:
                receipt.shopping_date = shopping_date
            
            # Handle file upload if present
            if 'picture' in request.FILES:
                picture_file = request.FILES['picture']
                print(f"Picture File Uploaded: {picture_file.name}")
                receipt.picture = picture_file
            
            receipt.save()
        
        # Save the updated item list
        item_list.save()
        
        print(f"Item ID {item_id} successfully updated!")
        print("="*50 + "\n")
        
        return redirect('/records/')
    
    except ItemList.DoesNotExist:
        return redirect('/records/')
    except Exception as e:
        print(f"Error updating item {item_id}: {str(e)}")
        return redirect('/records/')
