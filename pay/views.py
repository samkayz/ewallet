from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import auth
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from account.models import Merchant, Account, Transactions
import uuid


@csrf_exempt
def pay(request):
    if request.method == 'POST':
        desc = request.POST['item_name']
        amount = request.POST['amount']
        merchant = request.POST['merchant']
        success_url = request.POST['success']
        show_merchant = Merchant.objects.values('bus_name').get(api_test_key=merchant)['bus_name']
        m_username = Merchant.objects.values('bus_owner_username').get(api_test_key=merchant)['bus_owner_username']
        context = {'desc': desc, 'amount': amount, 'show_merchant': show_merchant, 'm_username': m_username,
                   'success_url': success_url}
    return render(request, 'pay.html', context)


def initiate(request):
    ref_no = uuid.uuid4().hex[:10].upper()
    if request.method == 'POST':
        amount = request.POST['amount']
        merchant = request.POST['merchant']
        username = request.POST['username']
        password = request.POST['password']
        success_url = request.POST['success_url']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            # you = Merchant.objects.values('bus_owner_username').get(bus_owner_username=username)['bus_owner_username']
            payee = Account.objects.values('bal').get(username=username)['bal']
            payer = Account.objects.values('bal').get(username=merchant)['bal']
            sb = (float(payee))
            rb = (float(payer))
            am = (float(amount))
            if am > sb:
                messages.info(request, 'Insufficient Balance')
                return redirect('error')
            elif merchant == username:
                messages.info(request, "You Can't Send Money to Yourself!!")
                return redirect('error')
            else:
                new = rb + am
                Account.objects.filter(username=merchant).update(bal=new)

                new_2 = sb - am
                Account.objects.filter(username=username).update(bal=new_2)

                trans = Transactions(sender=username,
                                     receiver=merchant,
                                     amount=amount,
                                     ref_no=ref_no, )
                trans.save()
                auth.logout(request)
                return HttpResponseRedirect("http://" + success_url)
        else:
            messages.info(request, 'Invalid Credentials')
            return redirect('error')
    else:
        return render(request, 'pay.html')


def error(request):
    return render(request, 'errors.html')


def success(request):
    return render(request, 'success.html')


def logout(request):
    auth.logout(request)
    return redirect('success')