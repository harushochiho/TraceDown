from django.http import Http404
from django.shortcuts import redirect

from main.models import ItemList


def delete_item(request, item_id):
    try:
        ItemList.objects.get(id=item_id).delete()
    except ItemList.DoesNotExist:
        print("Item does not exist")
    
    return redirect("/records/")