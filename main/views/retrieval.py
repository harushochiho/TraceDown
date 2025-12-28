from django.db.models import F
from django.shortcuts import render

from main.models import ItemList


def retrieval(request):
    all_receipts = ItemList.objects.select_related("receipt", "item", "category", "company", "is_on_sale",
                                                   "is_taxed").annotate(name=F("item__name"),
                                                                        category_name=F("category__name"),
                                                                        company_name=F("company__company_name"),
                                                                        tax=F("is_taxed__is_taxed"),
                                                                        on_sale=F("is_on_sale__is_on_sale"),
                                                                        shopping_date=F(
                                                                            "receipt__shopping_date"),
                                                                        picture=F("receipt__picture")).values(
        "shopping_date", "name", "price", "quantity", "remarks", "company_name", "category_name", "tax", "on_sale", "picture")
    return render(request, "read_items.html", {"items": all_receipts})
