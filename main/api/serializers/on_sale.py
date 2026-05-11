from django.core import serializers

from main.models import OnSale


class OnSaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnSale
        fields = '__all__'