import json
from pprint import pprint

from django.db.models import F
from django.shortcuts import render

from main.models import ItemList, Receipt


def retrieval(request):
    # all_receipts = ItemList.objects.select_related("receipt", "item", "category", "company", "is_on_sale",
    #                                                "is_taxed").annotate(name=F("item__name"),
    #                                                                     category_name=F("category__name"),
    #                                                                     company_name=F("company__company_name"),
    #                                                                     tax=F("is_taxed__is_taxed"),
    #                                                                     on_sale=F("is_on_sale__is_on_sale"),
    #                                                                     shopping_date=F(
    #                                                                         "receipt__shopping_date"),
    #                                                                     picture=F("receipt__picture")).values(
    #     "id", "shopping_date", "name", "price", "quantity", "remarks", "company_name", "category_name", "tax",
    #     "on_sale", "picture")
    temp_all_receipts = Receipt.objects.filter(item_list__id__isnull=False).annotate(item_list_id=F("item_list__id"),
                                                                                     item_name=F(
                                                                                         "item_list__item__name"),
                                                                                     price=F("item_list__price"),
                                                                                     quantity=F("item_list__quantity"),
                                                                                     remarks=F("item_list__remarks"),
                                                                                     category_name=F(
                                                                                         "item_list__category__name"),
                                                                                     company_name=F(
                                                                                         "item_list__company__company_name"),
                                                                                     tax=F(
                                                                                         "item_list__is_taxed__is_taxed"),
                                                                                     on_sale=F(
                                                                                         "item_list__is_on_sale__is_on_sale")).order_by(
        "-id").values(
        "id", "name", "item_list_id", "shopping_date", "item_name", "price", "quantity",
        "remarks", "company_name", "category_name", "tax",
        "on_sale", "picture")
    receipts_grouped = {}

    for item_receipt in temp_all_receipts:

        current_receipt = receipts_grouped.get(item_receipt.get("id"), {})

        if not current_receipt:
            current_receipt["picture"] = item_receipt.get("picture")
            current_receipt["name"] = item_receipt.get("name")
            current_receipt["shopping_date"] = item_receipt.get("shopping_date")
            current_receipt["items"] = []
            receipts_grouped[item_receipt.get("id")] = current_receipt

        new_item = dict()
        new_item["id"] = item_receipt.get("item_list_id")
        new_item["name"] = item_receipt.get("item_name")
        new_item["price"] = item_receipt.get("price")
        new_item["quantity"] = item_receipt.get("quantity")
        new_item["remarks"] = item_receipt.get("remarks")
        new_item["company_name"] = item_receipt.get("company_name")
        new_item["category_name"] = item_receipt.get("category_name")
        new_item["tax"] = item_receipt.get("tax")
        new_item["on_sale"] = item_receipt.get("on_sale")
        print(f"price: {item_receipt}, quantity: {new_item['quantity']}")
        receipts_grouped[item_receipt.get("id")]["items"].append(new_item)

    return render(request, "read_items.html", {"receipts": receipts_grouped})
