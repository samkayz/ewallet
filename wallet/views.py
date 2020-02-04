from django.shortcuts import render, redirect
from super.models import Details, Commission
from account.models import Account, Transactions, Subscription
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from wallet.settings import EMAIL_FROM
from super.models import Settings
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


def policy(request):
    return render(request, 'home/policy.html')


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
        s_email = request.POST['s_email']
        f_name = request.POST['f_name']
        charge = Commission.objects.values('pay_me').get(id=1)['pay_me']
        api_pk = Settings.objects.values('paystack_api').get(id=1)['paystack_api']
        f_charge = (float(charge))
        am = (float(amount))
        c_amt = am * (f_charge / 100)
        t_amt = am + c_amt
        request.session['ref_no'] = ref_no
        request.session['username'] = username
        request.session['amount'] = amount
        request.session['sender'] = sender
        request.session['s_email'] = s_email
        request.session['f_name'] = f_name
        request.session['c_amt'] = c_amt
        context = {'amount': amount, 'email': email, 'username': username,
                   'phone': phone, 'sender': sender, 'ref_no': ref_no, 'api_pk': api_pk,
                   'f_name': f_name, 's_email': s_email, 'c_amt': c_amt, 't_amt': t_amt}
        return render(request, 'pay-me.html', context)
    else:
        return render(request, 'pay-me.html')


def success(request):
    username = request.session['username']
    amount = request.session['amount']
    ref_no = request.session['ref_no']
    sender = request.session['sender']
    s_email = request.session['s_email']

    c_amt = request.session['c_amt']
    email = User.objects.values('email').get(username=username)['email']
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
    context = {'sender': sender, 'amount': amount, 'username': username}
    subject, from_email, to = 'Money From Pay-Me', EMAIL_FROM, email
    html_content = render_to_string('mail/payme.html',
                                    {'username': username, 'amount': amount, 'ref_no': ref_no,
                                     'sender': sender, 'new': new})
    text_content = strip_tags(html_content)
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    # Sender Email
    subject, from_email, to = 'Payment Confirmation', EMAIL_FROM, s_email
    html_content = render_to_string('mail/payme_sender.html',
                                    {'sender': sender, 'amount': amount,
                                     'username': username, 'c_amt': c_amt})
    text_content = strip_tags(html_content)
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    return render(request, 'success.html', context)


def fail(request):
    return render(request, 'fail.html')


def subscribe(request):
    if request.method == 'POST':
        sub = request.POST['subscribe']

        if Subscription.objects.filter(email=sub).exists():
            messages.info(request, 'You Already Subscribe to our Newsletter')
            return redirect('/index')
        else:
            s_save = Subscription(email=sub)
            s_save.save()
            messages.info(request, 'Thank You for Subscribing to our Newsletter')

            subject, from_email, to = 'Subscription', EMAIL_FROM, sub
            html_content = render_to_string('mail/news.html')
            text_content = strip_tags(html_content)
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            return redirect('/index')


def faq(request):
    return render(request, 'home/faq.html')


def term(request):
    return render(request, 'home/terms.html')
