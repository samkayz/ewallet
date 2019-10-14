from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.decorators import api_view
from account.models import Merchant, Account
from account.models import MerchantPayment
from account.api.serializers import MerchantSerializer, MerchantPaymentSerializer


@api_view(['GET', ])
def api_account_view(request, id):
    try:
        merchant = Merchant.objects.get(id=id)
    except Merchant.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = MerchantSerializer(merchant)
        return Response(serializer.data)


@api_view(['POST', ])
@csrf_exempt
def pay(request, id):
    try:
        merchant = MerchantPayment.objects.get(id=id)
    except Merchant.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    try:
        bal = Account.objects.get(id=id)
        Account.objects.filter(id=id).update(bal='2000.0')
    except Merchant.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'POST':
        serializer = MerchantPaymentSerializer(bal, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
