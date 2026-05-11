from django.core import serializers

from main.models import ItemList


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemList
        fields = '__all__'