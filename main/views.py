from django.shortcuts import render

# Create your views here.

def create_item(request):
    return render(request, "create_item.html")