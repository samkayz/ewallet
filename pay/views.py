from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import auth, User
from django.contrib import messages
from django.urls import reverse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from account.models import Merchant, Account, Transactions, VirtualCard
from super.models import Commission
from wallet.settings import EMAIL_FROM
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
        logo = Merchant.objects.values('bus_logo').get(api_test_key=merchant)['bus_logo']
        mode = Merchant.objects.values('w_p_charges').get(api_test_key=merchant)['w_p_charges']
        charge = Commission.objects.values('merchant').get(id=1)['merchant']
        f_charge = (float(charge))
        am = (float(amount))
        c_amt = am * (f_charge / 100)
        context = {'desc': desc, 'amount': amount, 'show_merchant': show_merchant, 'm_username': m_username,
                   'success_url': success_url, 'logo': logo, 'c_amt': c_amt, 'mode': mode}
        return render(request, 'pay.html', context)
    else:
        return render(request, 'pay.html')


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
            payee_email = User.objects.values('email').get(username=username)['email']
            merchant_email = User.objects.values('email').get(username=merchant)['email']
            payee = Account.objects.values('bal').get(username=username)['bal']
            payer = Account.objects.values('bal').get(username=merchant)['bal']
            merchant_name = Merchant.objects.values('bus_name').get(bus_owner_username=merchant)['bus_name']
            int_mode = Merchant.objects.values('int_mode').get(bus_owner_username=merchant)['int_mode']
            charge = Commission.objects.values('merchant').get(id=1)['merchant']
            mode = Merchant.objects.values('w_p_charges').get(bus_owner_username=merchant)['w_p_charges']
            f_charge = (float(charge))
            sb = (float(payee))
            rb = (float(payer))
            am = (float(amount))
            c_amt = am * (f_charge / 100)
            error = 'fail'
            if am > sb:
                return render(request, 'form.html', {'status': error,
                                                     'success_url': success_url})
            elif merchant == username:
                messages.info(request, "You Can't Send Money to Yourself!!")
                return redirect('error')
            else:
                if int_mode == 'live':
                    if mode == 'merchant':
                        c_charge = am - c_amt
                        new = rb + c_charge
                        Account.objects.filter(username=merchant).update(bal=new)

                        new_2 = sb - am
                        Account.objects.filter(username=username).update(bal=new_2)

                        trans = Transactions(sender=username,
                                             receiver=merchant,
                                             description='Merchant',
                                             amount=c_charge,
                                             ref_no=ref_no, )
                        trans.save()
                        auth.logout(request)
                        responseData = {
                            'amount': amount,
                            'ref_no': ref_no,
                            'username': username,
                            'email': payee_email,
                            'status': 'success'
                        }
                        report = JsonResponse(responseData)
                        #Payee Email
                        status = 'success'
                        subject, from_email, to = 'Purchase', EMAIL_FROM, payee_email
                        html_content = render_to_string('mail/vendor_payee.html',
                                                        {'username': username, 'amount': amount, 'ref_no': ref_no,
                                                         'merchant': merchant_name, 'new': new_2})
                        text_content = strip_tags(html_content)
                        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                        msg.attach_alternative(html_content, "text/html")
                        msg.send()

                        #Merchant Email
                        subject, from_email, to = 'Purchase', EMAIL_FROM, merchant_email
                        html_content = render_to_string('mail/vendor.html',
                                                        {'username': username, 'amount': amount, 'ref_no': ref_no,
                                                         'merchant': merchant_name, 'new': new})
                        text_content = strip_tags(html_content)
                        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                        msg.attach_alternative(html_content, "text/html")
                        msg.send()
                        return render(request, 'form.html', {'status': status,
                                                             'success_url': success_url,
                                                             'email': payee_email,
                                                             'amount': amount,
                                                             'ref_no': ref_no,
                                                             'username': username})
                    else:
                        new = rb + am
                        Account.objects.filter(username=merchant).update(bal=new)

                        c_charge = am + c_amt
                        new_2 = sb - c_charge
                        Account.objects.filter(username=username).update(bal=new_2)

                        trans = Transactions(sender=username,
                                             receiver=merchant,
                                             description='Merchant',
                                             amount=amount,
                                             ref_no=ref_no, )
                        trans.save()
                        auth.logout(request)
                        responseData = {
                            'amount': amount,
                            'ref_no': ref_no,
                            'username': username,
                            'email': payee_email,
                            'status': 'success'
                        }
                        report = JsonResponse(responseData)
                        # Payee Email
                        status = 'success'
                        subject, from_email, to = 'Purchase', EMAIL_FROM, payee_email
                        html_content = render_to_string('mail/vendor_payee.html',
                                                        {'username': username, 'amount': amount, 'ref_no': ref_no,
                                                         'merchant': merchant_name, 'new': new_2})
                        text_content = strip_tags(html_content)
                        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                        msg.attach_alternative(html_content, "text/html")
                        msg.send()

                        # Merchant Email
                        subject, from_email, to = 'Purchase', EMAIL_FROM, merchant_email
                        html_content = render_to_string('mail/vendor.html',
                                                        {'username': username, 'amount': amount, 'ref_no': ref_no,
                                                         'merchant': merchant_name, 'new': new})
                        text_content = strip_tags(html_content)
                        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                        msg.attach_alternative(html_content, "text/html")
                        msg.send()
                        return render(request, 'form.html', {'status': status,
                                                             'success_url': success_url,
                                                             'email': payee_email,
                                                             'amount': amount,
                                                             'ref_no': ref_no,
                                                             'username': username})
                else:
                    auth.logout(request)
                    responseData = {
                        'amount': amount,
                        'ref_no': ref_no,
                        'username': username,
                        'email': payee_email,
                        'status': 'success'
                    }
                    report = JsonResponse(responseData)
                    # Payee Email
                    status = 'success'
                    subject, from_email, to = 'Purchase', EMAIL_FROM, payee_email
                    html_content = render_to_string('mail/vendor_payee.html',
                                                    {'username': username, 'amount': amount, 'ref_no': ref_no,
                                                     'merchant': merchant_name})
                    text_content = strip_tags(html_content)
                    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()

                    # Merchant Email
                    subject, from_email, to = 'Purchase', EMAIL_FROM, merchant_email
                    html_content = render_to_string('mail/vendor.html',
                                                    {'username': username, 'amount': amount, 'ref_no': ref_no,
                                                     'merchant': merchant_name})
                    text_content = strip_tags(html_content)
                    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()
                    return render(request, 'form.html', {'status': status,
                                                         'success_url': success_url,
                                                         'email': payee_email,
                                                         'amount': amount,
                                                         'ref_no': ref_no,
                                                         'username': username})
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


def virtual(request):
    ref_no = uuid.uuid4().hex[:10].upper()
    if request.method == 'POST':
        amount = request.POST['amount']
        m_username = request.POST['merchant']
        success_url = request.POST['success_url']
        card_no = request.POST['card_no']
        pin = request.POST['pin']
        card_am = VirtualCard.objects.values('card_bal').get(card_no=card_no)['card_bal']
        merchant_email = User.objects.values('email').get(username=m_username)['email']
        merchant_name = Merchant.objects.values('bus_name').get(bus_owner_username=m_username)['bus_name']
        m_bal = Account.objects.values('bal').get(username=m_username)['bal']
        card_pin = VirtualCard.objects.values('pin').get(card_no=card_no)['pin']
        card_user = VirtualCard.objects.values('card_user').get(card_no=card_no)['card_user']
        int_mode = Merchant.objects.values('int_mode').get(bus_owner_username=m_username)['int_mode']
        mode = Merchant.objects.values('w_p_charges').get(bus_owner_username=m_username)['w_p_charges']
        payee_email = User.objects.values('email').get(username=card_user)['email']
        charge = Commission.objects.values('merchant').get(id=1)['merchant']
        f_charge = (float(charge))
        am = (float(amount))
        mb = (float(m_bal))
        cb = (float(card_am))
        c_amt = am * (f_charge / 100)
        error = 'fail'
        if pin == card_pin:
            if am > cb:
                return render(request, 'form.html', {'status': error,
                                                     'success_url': success_url})
            else:
                if int_mode == 'live':
                    if mode == 'merchant':
                        c_charge = am - c_amt
                        new = mb + c_charge
                        Account.objects.filter(username=m_username).update(bal=new)

                        new2 = cb - am
                        VirtualCard.objects.filter(card_no=card_no).update(card_bal=new2)
                        trans = Transactions(sender=card_user,
                                             receiver=m_username,
                                             description='Merchant',
                                             amount=c_charge,
                                             ref_no=ref_no, )
                        trans.save()
                        status = 'success'
                        subject, from_email, to = 'Purchase', EMAIL_FROM, payee_email
                        html_content = render_to_string('mail/vendor_payee.html',
                                                        {'username': card_user, 'amount': amount, 'ref_no': ref_no,
                                                         'merchant': merchant_name, 'new': new2})
                        text_content = strip_tags(html_content)
                        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                        msg.attach_alternative(html_content, "text/html")
                        msg.send()

                        # Merchant Email
                        subject, from_email, to = 'Purchase', EMAIL_FROM, merchant_email
                        html_content = render_to_string('mail/vendor.html',
                                                        {'username': card_user, 'amount': amount, 'ref_no': ref_no,
                                                         'merchant': merchant_name, 'new': new})
                        text_content = strip_tags(html_content)
                        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                        msg.attach_alternative(html_content, "text/html")
                        msg.send()
                        return render(request, 'form.html', {'status': status,
                                                             'success_url': success_url,
                                                             'email': payee_email,
                                                             'amount': amount,
                                                             'ref_no': ref_no,
                                                             'username': card_user})
                    else:
                        new = mb + am
                        Account.objects.filter(username=m_username).update(bal=new)

                        c_charge = am + c_amt
                        new2 = cb - c_charge
                        VirtualCard.objects.filter(card_no=card_no).update(card_bal=new2)

                        trans = Transactions(sender=card_user,
                                             receiver=m_username,
                                             description='Merchant',
                                             amount=amount,
                                             ref_no=ref_no, )
                        trans.save()
                        status = 'success'
                        subject, from_email, to = 'Purchase', EMAIL_FROM, payee_email
                        html_content = render_to_string('mail/vendor_payee.html',
                                                        {'username': card_user, 'amount': amount, 'ref_no': ref_no,
                                                         'merchant': merchant_name, 'new': new2})
                        text_content = strip_tags(html_content)
                        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                        msg.attach_alternative(html_content, "text/html")
                        msg.send()

                        # Merchant Email
                        subject, from_email, to = 'Purchase', EMAIL_FROM, merchant_email
                        html_content = render_to_string('mail/vendor.html',
                                                        {'username': card_user, 'amount': amount, 'ref_no': ref_no,
                                                         'merchant': merchant_name, 'new': new})
                        text_content = strip_tags(html_content)
                        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                        msg.attach_alternative(html_content, "text/html")
                        msg.send()
                        return render(request, 'form.html', {'status': status,
                                                             'success_url': success_url,
                                                             'email': payee_email,
                                                             'amount': amount,
                                                             'ref_no': ref_no,
                                                             'username': card_user})
                else:
                    status = 'success'
                    subject, from_email, to = 'Purchase', EMAIL_FROM, payee_email
                    html_content = render_to_string('mail/vendor_payee.html',
                                                    {'username': card_user, 'amount': amount, 'ref_no': ref_no,
                                                     'merchant': m_username})
                    text_content = strip_tags(html_content)
                    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()

                    # Merchant Email
                    subject, from_email, to = 'Purchase', EMAIL_FROM, merchant_email
                    html_content = render_to_string('mail/vendor.html',
                                                    {'username': card_user, 'amount': amount, 'ref_no': ref_no,
                                                     'merchant': merchant_name})
                    text_content = strip_tags(html_content)
                    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()
                    return render(request, 'form.html', {'status': status,
                                                         'success_url': success_url,
                                                         'email': payee_email,
                                                         'amount': amount,
                                                         'ref_no': ref_no,
                                                         'username': card_user})
        else:
            messages.info(request, 'Invalid Credentials')
            return redirect('error')
    return render(request, 'pay.html')
