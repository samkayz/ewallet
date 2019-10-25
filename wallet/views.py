from django.shortcuts import render, redirect
from super.models import Details
from account.models import Account, Transactions
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import uuid


def landing(request):
    show = Details.objects.all().get(id=1)
    context = {'show': show}
    return render(request, 'home/landing.html', context)


def about(request):
    show = Details.objects.all().get(id=1)
    context = {'show': show}
    return render(request, 'home/about.html', context)


def service(request):
    return render(request, 'home/service.html')


def contact(request):
    show = Details.objects.all().get(id=1)
    context = {'show': show}
    return render(request, 'home/contact.html', context)


def payme(request, username):
    if Account.objects.filter(username=username).exists():
        first_name = Account.objects.values('first_name').get(username=username)['first_name']
        last_name = Account.objects.values('last_name').get(username=username)['last_name']
        phone = Account.objects.values('phone_no').get(username=username)['phone_no']
        email = User.objects.values('email').get(username=username)['email']
        context = {'first_name': first_name, 'last_name': last_name, 'email': email,
                   'username': username, 'phone': phone}
        return render(request, 'amount.html', context)
    else:
        return redirect('not-found')


def error(request):
    return render(request, 'not_found.html')


def initiate(request):
    ref_no = uuid.uuid4().hex[:10].upper()
    if request.method == 'POST':
        amount = request.POST['amount']
        email = request.POST['email']
        username = request.POST['username']
        phone = request.POST['phone']
        sender = request.POST['sender']

        request.session['ref_no'] = ref_no
        request.session['username'] = username
        request.session['amount'] = amount
        request.session['sender'] = sender
        context = {'amount': amount, 'email': email, 'username': username,
                   'phone': phone, 'sender': sender, 'ref_no': ref_no}
        return render(request, 'payme.html', context)
    else:
        return render(request, 'payme.html')


def success(request):
    username = request.session['username']
    amount = request.session['amount']
    ref_no = request.session['ref_no']
    sender = request.session['sender']
    bal = Account.objects.values('bal').get(username=username)['bal']
    sb = (float(bal))
    am = (float(amount))
    new = sb + am
    Account.objects.filter(username=username).update(bal=new)
    messages.info(request, 'Transaction Successful')
    trans = Transactions(sender=sender, receiver=username, amount=am, ref_no=ref_no, )
    trans.save()
    del request.session['username']
    del request.session['amount']
    del request.session['ref_no']
    del request.session['sender']
    return render(request, 'amount.html')


def fail(request):
    return render(request, 'fail.html')
