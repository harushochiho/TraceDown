from django.apps import AppConfig


def seeding_data():
    print('seeding data')
    from .models import Tax, OnSale
    
    if not Tax.objects.exists():
        print('seeding tax data')
        Tax.objects.create(is_taxed=True, desc="Yes").save()
        Tax.objects.create(is_taxed=False, desc="No").save()
    
    if not OnSale.objects.exists():
        print('seeding on sale data')
        OnSale.objects.create(is_on_sale=True, desc="Yes").save()
        OnSale.objects.create(is_on_sale=False, desc="No").save()

    print('finished seeding data')
    
class MainConfig(AppConfig):
    name = 'main'

    def ready(self):
        print('Ready')