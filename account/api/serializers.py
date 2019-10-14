from rest_framework import serializers
from account.models import Merchant, MerchantPayment


class MerchantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Merchant
        fields = ['id', 'bus_owner_username',
                  'bus_name', 'bus_address',
                  'bus_no', 'bus_website',
                  'api_test_key', 'api_live_key']


class MerchantPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MerchantPayment
        fields = ['id', 'bus_owner_username',
                  'payee', 'amount']

