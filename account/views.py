from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from .models import Account, Transactions, Voucher, Ticket, Merchant, Bank, Withdraw, Invoice, Banks, VirtualCard
from .models import Customer, Staff
from super.models import Resolution, Settings, Commission
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db.models import Sum
from wallet.settings import EMAIL_FROM
from typing import Union
from collections import namedtuple
import random
import string
import uuid
import datetime
from datetime import datetime
import csv
import io


# Login view function that handle all the login
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            request.session.set_expiry(300)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid Credentials')
            return redirect('login')
    else:
        return render(request, 'login.html')


# Registration View Function that handle all the Registration
def register(request):
    N = 5
    res = ''.join(random.choices(string.digits, k=N))
    cus_id = str(res)
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        phone_no = request.POST['phone_no']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username taken')
                return redirect('register')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email Taken')
                return redirect('register')
            elif Account.objects.filter(phone_no=phone_no).exists():
                messages.error(request, 'Mobile Number Used')
                return redirect('register')
            else:
                user = User.objects.create_user(username=username,
                                                password=password1,
                                                email=email,
                                                first_name=first_name,
                                                last_name=last_name,
                                                )
                users = Account(username=username,
                                first_name=first_name,
                                last_name=last_name,
                                phone_no=phone_no,
                                customer_id=cus_id,
                                bal='0',
                                status='unhold')
            users.save()
            user.save()
            # messages.info(request, 'Account Created Successfully, Kindly login with Your Username and Password')
            subject, from_email, to = 'Account Registration', EMAIL_FROM, email
            html_content = render_to_string('mail/signup.html',
                                            {'first_name': first_name, 'cus_id': cus_id, 'username': username})
            text_content = strip_tags(html_content)
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            user = auth.authenticate(username=username, password=password1)
            auth.login(request, user)
            return redirect('dashboard')
        else:
            messages.info(request, 'Password not Matching')
            return redirect('register')

    else:
        return render(request, 'register.html')


# Dashboard view function
@login_required(login_url='login')
def dashboard(request):
    c_user = request.user.username
    show = Account.objects.all().get(username=c_user)
    shows = VirtualCard.objects.filter(card_user=c_user)
    # check = VirtualCard.objects.values('card_user').get(card_user=c_user)['card_user']
    vendor = Transactions.objects.filter(receiver=c_user).filter(
        description='Merchant').aggregate(Sum('amount'))['amount__sum']
    context = {'show': show, 'vendor': vendor, 'shows': shows}
    return render(request, 'dashboard.html', context)


# Logout function the terminate all the login session
def logout(request):
    auth.logout(request)
    return redirect('login')


# Transfer function that handle the transfer of money within the system
@login_required(login_url='login')
def transfer(request):
    ref_no = uuid.uuid4().hex[:10].upper()
    base_date_time = datetime.now()
    now = (datetime.strftime(base_date_time, "%Y-%m-%d %H:%M %p"))
    if request.method == 'POST':
        s_username = request.POST['s_username']
        r_number = request.POST['r_number']
        amount = request.POST['amount']
        bal = Account.objects.values('bal').get(phone_no=r_number)['bal']
        s_bal = Account.objects.values('bal').get(username=s_username)['bal']
        first_name = Account.objects.values('first_name').get(username=s_username)['first_name']
        r_first_name = Account.objects.values('first_name').get(phone_no=r_number)['first_name']
        r_mail = User.objects.values('email').get(username=s_username)['email']
        r_username = Account.objects.values('username').get(phone_no=r_number)['username']
        m_email = User.objects.values('email').get(username=r_username)['email']
        show = Account.objects.values().get(phone_no=r_number)['username']
        status = Account.objects.values('status').get(username=s_username)['status']
        r_status = Account.objects.values('status').get(phone_no=r_number)['status']
        charge = Commission.objects.values('transfer').get(id=1)['transfer']

        # print("Hello: ", show)
        f_charge = (float(charge))
        sb = (float(s_bal))
        rb = (float(bal))
        am = (float(amount))
        c_amt = am * (f_charge / 100)
        if status == 'hold':
            messages.warning(request, 'Your Account is on Hold, Please contact our agent')
        elif r_status == 'hold':
            messages.warning(request, "This Customer Can't receive Money at the Moment")
        elif am > sb:
            messages.warning(request, 'Insufficient Balance')
        elif s_username == show:
            messages.warning(request, "You Can't Send Money to Yourself!!")
        else:
            new = rb + am
            Account.objects.filter(phone_no=r_number).update(bal=new)

            new_2 = (sb - (am + c_amt))
            Account.objects.filter(username=s_username).update(bal=new_2)

            trans = Transactions(sender=s_username,
                                 receiver=show,
                                 amount=amount,
                                 description='FT',
                                 ref_no=ref_no,)
            trans.save()
            messages.success(request, "Transaction Successful!!")

            # Sender Email Notification
            subject, from_email, to = 'Fund Transfer', EMAIL_FROM, r_mail
            html_content = render_to_string('mail/s_mail.html',
                                            {'first_name': first_name, 'new_2': new_2, 'ref_no': ref_no, 'amount': am,
                                             'receiver': r_number, 'c_amt': c_amt, 'date': now})
            text_content = strip_tags(html_content)
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            #         Receiver Email Notification
            subject, from_email, to = 'Fund Transfer', EMAIL_FROM, m_email
            html_content = render_to_string('mail/r_mail.html',
                                            {'r_first_name': r_first_name, 'new': new, 'ref_no': ref_no, 'amount': am,
                                             'sender': first_name, 'date': now})
            text_content = strip_tags(html_content)
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
    return render(request, 'transfer.html')


# Verify function the verify the user of the wallet
@login_required(login_url='login')
def verify(request):
    if request.method == 'POST':
        r_number = request.POST['number']
        num = Account.objects.filter(phone_no=r_number).exists()
        if num:
            check = Account.objects.all().get(phone_no=r_number)
            charge = Commission.objects.values('transfer').get(id=1)['transfer']
            cont = {'check': check, 'num': num, 'charge': charge}
            return render(request, 'transfer.html', cont)
        else:
            messages.error(request, 'Mobile Number Not Found')
            return redirect('transfer')

    return render(request, 'transfer.html')


# Setting view function
@login_required(login_url='login')
def settings(request):
    c_user = request.user.username
    if Merchant.objects.filter(bus_owner_username=c_user).exists():
        s_show = Merchant.objects.all().get(bus_owner_username=c_user)
        show = Account.objects.values('phone_no').get(username=c_user)['phone_no']
        i_mode = Merchant.objects.values('int_mode').get(bus_owner_username=c_user)['int_mode']
        w_p_charges = Merchant.objects.values('w_p_charges').get(bus_owner_username=c_user)['w_p_charges']
        cus_id = Account.objects.values('customer_id').get(username=c_user)['customer_id']
        context = {'s_show': s_show, 'show': show, 'cus_id': cus_id, 'i_mode': i_mode, 'w_p_charges': w_p_charges}
        return render(request, 'settings.html', context)
    else:
        return redirect('api')


# The view that handle all the transaction activity
@login_required(login_url='login')
def activity(request):
    c_user = request.user.username
    show = Transactions.objects.filter(Q(sender=c_user) | Q(receiver=c_user)).order_by('date')[::-1]
    # print("Hello:", show)
    context = {'show': show}
    return render(request, 'activity.html', context)


# Voucher View function that handle the voucher generation
@login_required(login_url='login')
def voucher(request):
    N = 10
    code = ''.join(random.choices(string.digits, k=N))
    ref_no = uuid.uuid4().hex[:10].upper()
    c_user = request.user.username
    if request.method == 'POST':
        # v_username = request.POST['v_username']
        amount = request.POST['amount']
        s_bal = Account.objects.values('bal').get(username=c_user)['bal']
        status = Account.objects.values('status').get(username=c_user)['status']
        sb = (float(s_bal))
        am = (float(amount))

        if status == "hold":
            messages.warning(request, 'Your Account is Currently on Hold ')
        elif am > sb:
            messages.error(request, 'Insufficient Balance')
        else:
            new_2 = sb - am
            Account.objects.filter(username=c_user).update(bal=new_2)
            v_save = Voucher(v_creator=c_user,
                             v_code=code,
                             v_amount=am,
                             ref_no=ref_no,
                             v_status='open',
                             )
            trans = Transactions(sender=c_user,
                                 receiver='voucher',
                                 amount=amount,
                                 description='Voucher',
                                 ref_no=ref_no, )
            trans.save()
            v_save.save()
            messages.success(request, "Transaction Successful!!")
    show = Voucher.objects.filter(Q(v_creator=c_user)).order_by('-v_date').reverse()
    context = {'show': show}
    return render(request, 'voucher.html', context)


# View function that handle voucher redeeming
@login_required(login_url='login')
def load_voucher(request):
    ref_no = uuid.uuid4().hex[:10].upper()
    base_date_time = datetime.now()
    now = (datetime.strftime(base_date_time, "%Y-%m-%d %H:%M %p"))
    c_user = request.user.username
    if request.method == 'POST':
        v_code = request.POST['v_code']
        l_username = request.POST['l_username']
        if Voucher.objects.filter(v_code=v_code).exists():
            v_am = Voucher.objects.values('v_amount').get(v_code=v_code)['v_amount']
            status = Voucher.objects.values('v_status').get(v_code=v_code)['v_status']
            loader = Voucher.objects.values('v_creator').get(v_code=v_code)['v_creator']
            bal = Account.objects.values('bal').get(username=c_user)['bal']
            a_status = Account.objects.values('status').get(username=c_user)['status']
            sb = (float(bal))
            am = (float(v_am))

            if a_status == "hold":
                messages.warning(request, "Your Account is Currently on Hold")
                return redirect('load_voucher')
            if status == 'close':
                messages.error(request, "Voucher Used")
                return redirect('load_voucher')
            elif loader == l_username:
                messages.warning(request, "You Cant load the Voucher you Created")
                return redirect('load_voucher')
            else:
                new = sb + am
                Account.objects.filter(username=l_username).update(bal=new)
                Voucher.objects.filter(v_code=v_code).update(v_status='close', v_loader=c_user, v_date_load=now)
                messages.success(request, "Transaction Successful!!")

                trans = Transactions(sender='Voucher', receiver=l_username, amount=am,
                                     description='Voucher', ref_no=ref_no,)
                trans.save()
                return redirect('load_voucher')
        else:
            messages.info(request, "Invalid Code/Code Doesn't Exist!!")
            return redirect('load_voucher')
    show = Voucher.objects.filter(Q(v_creator=c_user))
    context = {'show': show}
    return render(request, 'load_voucher.html', context)


@login_required(login_url='login')
def ticket(request):
    N = 6
    ticket_id = ''.join(random.choices(string.digits, k=N))
    c_user = request.user.username
    if request.method == 'POST':
        subject = request.POST['subject']
        category = request.POST['category']
        content = request.POST['content']
        priority = request.POST['priority']

        t_save = Ticket(subject=subject,
                        category=category,
                        owner=c_user,
                        content=content,
                        priority=priority,
                        status='open',
                        ticket_id=ticket_id,)
        t_save.save()
        messages.info(request, "Ticket Created")

    show = Ticket.objects.filter(Q(owner=c_user))
    context = {'show': show}
    return render(request, 'ticket.html', context)


def compose(request):
    return render(request, 'compose.html')


@login_required(login_url='login')
def dispute(request):
    c_user = request.user.username
    show = Ticket.objects.filter(Q(owner=c_user))
    context = {'show': show}
    return render(request, 'dispute.html', context)


@login_required(login_url='login')
def merchant(request):
    c_user = request.user.username
    if request.method == 'POST':
        b_name = request.POST['b_name']
        b_address = request.POST['b_address']
        b_email = request.POST['b_email']
        b_tel = request.POST['b_tel']
        b_url = request.POST['b_url']
        bus_logo = request.FILES['bus_logo']

        if Account.objects.values('status').get(username=c_user)['status'] == "hold":
            messages.info(request, "You Account is Currently o Hold")
            return redirect('settings')
        elif Merchant.objects.filter(bus_owner_username=c_user).exists():
            messages.warning(request, "You are a Merchant Already")
            return redirect('settings')
        else:
            b_save = Merchant(bus_owner_username=c_user, bus_name=b_name, bus_address=b_address, bus_email=b_email,
                              bus_no=b_tel, bus_website=b_url, bus_logo=bus_logo)
            b_save.save()
            messages.success(request, "Merchant Registration Successful")
            return redirect('settings')
    show = Account.objects.values('phone_no').get(username=c_user)['phone_no']
    context = {'show': show}
    return render(request, 'settings.html', context)


@login_required(login_url='login')
def api(request):
    c_user = request.user.username
    api_test = uuid.uuid4().hex[:50].lower()
    api_live = uuid.uuid4().hex[:50].lower()
    if request.method == 'POST':
        user = request.POST['user']
        if Account.objects.values('status').get(username=c_user)['status'] == "hold":
            messages.error(request, "You Account is Currently o Hold")
            return redirect('settings')
        elif Merchant.objects.filter(bus_owner_username=c_user).exists():
            Merchant.objects.filter(bus_owner_username=user).update(api_test_key=api_test, api_live_key=api_live)
            messages.success(request, "Please Find Your API key on API Tab")
            return redirect('settings')
        else:
            messages.warning(request, "You have to be a Merchant before you can use our API")
            return redirect('settings')
    show = Account.objects.values('phone_no').get(username=c_user)['phone_no']
    cus_id = Account.objects.values('customer_id').get(username=c_user)['customer_id']
    context = {'show': show, 'cus_id': cus_id}
    return render(request, 'settings.html', context)


@login_required(login_url='login')
def reply(request, ticket_id):
    show = Ticket.objects.filter(Q(ticket_id=ticket_id))
    r_show = Resolution.objects.filter(Q(ticket_id=ticket_id))
    get_content = Ticket.objects.all().get(ticket_id=ticket_id)
    context = {'show': show, 'r_show': r_show, 'get_content': get_content}
    return render(request, 'ticket.html', context)


@login_required(login_url='login')
def resolution(request):
    if request.method == 'POST':
        ticket_id = request.POST['ticket_id']
        subject = request.POST['subject']
        category = request.POST['category']
        content = request.POST['content']

        t_save = Resolution(ticket_id=ticket_id, subject=subject, category=category, content=content)
        t_save.save()
        # messages.info(request, "Reply Successful!!")
        return redirect('ticket')
    return render(request, 'ticket.html')


@login_required(login_url='login')
def bank(request):
    c_user = request.user.username
    if request.method == 'POST':
        acct_name = request.POST['acct_name']
        acct_no = request.POST['acct_no']
        bank_name = request.POST['bank_name']
        status = Account.objects.values('status').get(username=c_user)['status']
        if status == "hold":
            messages.warning(request, "You Account is Currently o Hold")
            return redirect('bank')
        else:
            s_bank = Bank(username=c_user, account_name=acct_name, account_no=acct_no, bank_name=bank_name)
            s_bank.save()
            messages.success(request, "Added Successful!!")
            return redirect('bank')
    all_bank = Banks.objects.filter()
    show = Bank.objects.filter(Q(username=c_user))
    context = {'show': show, 'bank': all_bank}
    return render(request, 'add_bank_acc.html', context)


@login_required(login_url='login')
def delete(request, id):
    Bank.objects.filter(id=id).delete()
    messages.info(request, 'Account Deleted')
    return redirect('bank')


@login_required(login_url='login')
def withdraw(request):
    base_date_time = datetime.now()
    now = (datetime.strftime(base_date_time, "%Y-%m-%d %H:%M %p"))
    ref_no = uuid.uuid4().hex[:10].upper()
    c_user = request.user.username
    if request.method == 'POST':
        acct_no = request.POST['bank_name']
        amount = request.POST['amount']
        acct_name = Bank.objects.values('account_name').get(account_no=acct_no)['account_name']
        bank_name = Bank.objects.values('bank_name').get(account_no=acct_no)['bank_name']
        bal = Account.objects.values('bal').get(username=c_user)['bal']
        status = Account.objects.values('status').get(username=c_user)['status']
        first_name = User.objects.values('first_name').get(username=c_user)['first_name']
        email = User.objects.values('email').get(username=c_user)['email']
        sb = (float(bal))
        am = (float(amount))

        if status == "hold":
            messages.error(request, 'Sorry, You Account is on Hold')
            return redirect('withdraw')
        elif am <= 0:
            messages.warning(request, 'Invalid Transaction')
            return redirect('withdraw')
        elif sb < am:
            messages.warning(request, 'Low Balance ')
            return redirect('withdraw')
        elif am < 1000.0:
            messages.warning(request, 'Withdraw Minimum is 1,000 ')
            return redirect('withdraw')
        else:
            new = sb-am
            Account.objects.filter(username=c_user).update(bal=new)
            s_withdraw = Withdraw(username=c_user, amount=amount, acct_name=acct_name, acct_no=acct_no,
                                  bank_name=bank_name, status='pending', ref_no=ref_no,)
            trans = Transactions(sender=c_user,
                                 receiver='Withdrawal',
                                 amount=amount,
                                 description='Debit',
                                 ref_no=ref_no, )
            trans.save()
            s_withdraw.save()
            messages.success(request, "Successful!!")
            subject, from_email, to = 'Fund Withdrawal', EMAIL_FROM, email
            html_content = render_to_string('mail/withdraw.html',
                                            {'bank_name': bank_name, 'amount': amount,
                                             'new': new, 'ref_no': ref_no, 'date': now,
                                             'first_name': first_name, 'acct_name': acct_name, 'acct_no': acct_no})
            text_content = strip_tags(html_content)
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
    show = Bank.objects.filter(Q(username=c_user))
    u_withdraw = Withdraw.objects.filter(Q(username=c_user))
    context = {'show': show, 'u_withdraw': u_withdraw}
    return render(request, 'withdraw.html', context)


@login_required(login_url='login')
def deposit(request):
    ref_no = uuid.uuid4().hex[:10].upper()
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        amount = request.POST['amount']
        show = Account.objects.values().get(username=username)['phone_no']
        request.session['ref_no'] = ref_no
        request.session['username'] = username
        request.session['amount'] = amount
        context = {'username': username, 'email': email, 'amount': amount, 'show': show, 'ref_no': ref_no}
        return render(request, 'confirm.html', context)
    else:
        return render(request, 'deposit.html')


def airtime_verify(request, reference):
    return render(request, 'airtime.html')


@login_required(login_url='login')
def airtime(request):
    ref_no = uuid.uuid4().hex[:10].upper()
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        amount = request.POST['amount']
        show = Account.objects.values().get(username=username)['phone_no']

        request.session['ref_no'] = ref_no
        request.session['username'] = username
        request.session['amount'] = amount
        context = {'username': username, 'email': email, 'amount': amount, 'show': show, 'ref_no': ref_no}
        return render(request, 'airtime_confirm.html', context)
    else:
        return render(request, 'airtime.html')


def airtime_confirm(request):
    return render(request, 'airtime_confirm.html')


@login_required(login_url='login')
def confirm(request):
    return render(request, 'confirm.html')


# @login_required(login_url='login')
# def payment(request):
#     username = request.session['username']
#     amount = request.session['amount']
#     ref_no = request.session['ref_no']
#     bal = Account.objects.values('bal').get(username=username)['bal']
#     sb = (float(bal))
#     am = (float(amount))
#     new = sb + am
#     Account.objects.filter(username=username).update(bal=new)
#     messages.info(request, 'Transaction Successful')
#     trans = Transactions(sender='Card Payment', receiver=username, amount=am, description='Deposit', ref_no=ref_no, )
#     trans.save()
#     del request.session['username']
#     del request.session['amount']
#     del request.session['ref_no']
#     return render(request, 'deposit.html')


@login_required(login_url='login')
def invoice_verify(request):
    if request.method == 'POST':
        username = request.POST['username']
        check_user = Account.objects.filter(username=username).exists()
        if check_user:
            check = Account.objects.all().get(username=username)
            cont = {'check': check, 'check_user': check_user}
            return render(request, 'invoice.html', cont)
        else:
            messages.error(request, 'User Not Found')
            return redirect('invoice')


@login_required(login_url='login')
def invoice(request):
    base_date_time = datetime.now()
    now = (datetime.strftime(base_date_time, "%Y-%m-%d %H:%M %p"))
    c_user = request.user.username
    if request.method == 'POST':
        s_username = request.POST['s_username']
        r_username = request.POST['r_username']
        amount = request.POST['amount']
        content = request.POST['content']
        status = Account.objects.values('status').get(username=c_user)['status']
        r_status = Account.objects.values('status').get(username=r_username)['status']
        r_email = User.objects.values('email').get(username=r_username)['email']
        s_email = User.objects.values('email').get(username=s_username)['email']

        if status == "hold":
            messages.warning(request, 'Your Account is on hold. Kindly contact our Agent')
            return redirect('invoice')
        elif r_status == "hold":
            messages.warning(request, "This Customer Can't receive Money at the Moment")
            return redirect('invoice')
        elif c_user == r_username:
            messages.error(request, "Please You Can't Send Invoice to Yourself")
            return redirect('invoice')
        else:
            s_invoice = Invoice(sender=s_username, receiver=r_username, amount=amount, content=content,
                                status='pending', action='Pay Now')
            s_invoice.save()
        messages.success(request, 'Invoice Created')
        # Sender
        subject, from_email, to = 'Invoice', EMAIL_FROM, s_email
        html_content = render_to_string('mail/s_invoice.html',
                                        {'r_username': r_username, 's_username': s_username,
                                         'amount': amount, 'date': now})
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        #     Receiver
        subject, from_email, to = 'Invoice', EMAIL_FROM, r_email
        html_content = render_to_string('mail/r_invoice.html',
                                        {'r_username': r_username, 's_username': s_username,
                                         'amount': amount, 'content': content, 'date': now})
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    show = Invoice.objects.filter(Q(sender=c_user))
    context = {'show': show}
    return render(request, 'invoice.html', context)


@login_required(login_url='login')
def pay_invoice(request):
    c_user = request.user.username
    show = Invoice.objects.filter(Q(receiver=c_user))
    context = {'show': show}
    return render(request, 'pay_invoice.html', context)


@login_required(login_url='login')
def success(request, id):
    base_date_time = datetime.now()
    now = (datetime.strftime(base_date_time, "%Y-%m-%d %H:%M %p"))
    ref_no = uuid.uuid4().hex[:10].upper()
    r_username = Invoice.objects.values('receiver').get(id=id)['receiver']
    s_username = Invoice.objects.values('sender').get(id=id)['sender']
    r_acct = Account.objects.values('bal').get(username=r_username)['bal']
    s_acct = Account.objects.values('bal').get(username=s_username)['bal']
    amount = Invoice.objects.values('amount').get(id=id)['amount']
    status = Account.objects.values('status').get(username=r_username)['status']
    s_email = User.objects.values('email').get(username=s_username)['email']
    s_act = (float(s_acct))
    r_act = (float(r_acct))
    am = (float(amount))

    if status == "hold":
        messages.error(request, 'Your Account is on hold. Kindly contact our Agent')
        return redirect('pay-invoice')
    elif Invoice.objects.values('status').get(id=id)['status'] == 'paid':
        messages.error(request, 'Invoice Paid Already')
        return redirect('pay-invoice')
    elif Invoice.objects.values('status').get(id=id)['status'] == 'reject':
        messages.error(request, 'Invoice Already Rejected')
        return redirect('pay-invoice')
    else:
        new1 = r_act - am
        Account.objects.filter(username=r_username).update(bal=new1)

        new2 = s_act + am
        Account.objects.filter(username=s_username).update(bal=new2)

        Invoice.objects.filter(id=id).update(status='paid', date_paid=now, action='Paid')

        s_invoice = Transactions(sender=r_username,
                                 receiver=s_username,
                                 amount=amount,
                                 description="Invoice",
                                 ref_no=ref_no)
        s_invoice.save()
        messages.success(request, "You Have Successfully Paid The Invoice")
        subject, from_email, to = 'Invoice', EMAIL_FROM, s_email
        html_content = render_to_string('mail/s_mail_invoice.html',
                                        {'r_username': r_username, 's_username': s_username,
                                         'amount': amount, 'ref_no': ref_no, 'new2': new2, 'date': now})
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return redirect('pay-invoice')


@login_required(login_url='login')
def reject(request, id):
    c_user = request.user.username
    base_date_time = datetime.now()
    now = (datetime.strftime(base_date_time, "%Y-%m-%d %H:%M %p"))
    if Account.objects.values('status').get(username=c_user)['status'] == "hold":
        messages.error(request, 'Your Account is on hold')
        return redirect('pay-invoice')
    elif Invoice.objects.values('status').get(id=id)['status'] == 'reject':
        messages.error(request, 'Invoice Already Rejected')
        return redirect('pay-invoice')
    elif Invoice.objects.values('status').get(id=id)['status'] == 'paid':
        messages.warning(request, 'Invoice Already Paid')
        return redirect('pay-invoice')
    else:
        Invoice.objects.filter(id=id).update(status='reject', date_paid=now)
        messages.success(request, 'Invoice Rejected')
        return redirect('pay-invoice')


@login_required(login_url='login')
def paid_invoice(request):
    c_user = request.user.username
    show = Invoice.objects.filter(Q(sender=c_user))
    context = {'show': show}
    return render(request, 'paid_invoice.html', context)


@login_required(login_url='login')
def load(request):
    return render(request, 'load.html')


@login_required(login_url='login')
def deposit(request):
    ref_no = uuid.uuid4().hex[:10].upper()
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        amount = request.POST['amount']
        show = Account.objects.values('phone_no').get(username=username)['phone_no']
        status = Account.objects.values('status').get(username=username)['status']
        api_pk = Settings.objects.values('paystack_api').get(id=1)['paystack_api']
        charge = Commission.objects.values('deposit').get(id=1)['deposit']
        f_charge = (float(charge))
        am = (float(amount))
        c_amt = am * (f_charge / 100)
        t_amt = am + c_amt
        if status == "hold":
            messages.error(request, "You Account is Currently o Hold")
            return redirect('deposit')
        else:
            request.session['username'] = username
            request.session['amount'] = amount
            request.session['ref_no'] = ref_no
            request.session['t_amt'] = t_amt
            request.session['c_amt'] = c_amt
            context = {'username': username, 'email': email, 't_amt': t_amt,
                       'ref_no': ref_no, 'show': show, 'amount': amount,
                       'c_amt': c_amt, 'charge': charge, 'api_pk': api_pk}
            return render(request, 'confirm.html', context)
    else:
        return render(request, 'deposit.html')


@login_required(login_url='login')
def payment(request):
    base_date_time = datetime.now()
    now = (datetime.strftime(base_date_time, "%Y-%m-%d %H:%M %p"))
    amount = request.session['amount']
    username = request.session['username']
    ref_no = request.session['ref_no']
    t_amt = request.session['t_amt']
    c_amt = request.session['c_amt']
    balance = Account.objects.values('bal').get(username=username)['bal']
    acct_bal = (float(balance))
    amt = (float(amount))
    new = acct_bal + amt
    Account.objects.filter(username=username).update(bal=new)
    email = User.objects.values('email').get(username=username)['email']
    first_name = User.objects.values('first_name').get(username=username)['first_name']
    t_reg = Transactions(sender='Card Deposit', receiver=username, amount=amount, description='Deposit', ref_no=ref_no)
    t_reg.save()
    messages.success(request, 'Transaction Successful')
    subject, from_email, to = 'Fund Deposit', EMAIL_FROM, email
    html_content = render_to_string('mail/deposit.html',
                                    {'username': username, 'amount': amount,
                                     'new': new, 'ref_no': ref_no, 'date': now,
                                     'first_name': first_name, 't_amt': t_amt, 'c_amt': c_amt})
    text_content = strip_tags(html_content)
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    return redirect('deposit')


@login_required(login_url='login')
def fail(request):
    messages.error(request, 'Transaction Fail')
    return redirect('deposit')


@login_required(login_url='login')
def int_mode(request):
    if request.method == 'POST':
        user = request.POST['user']
        i_mode = request.POST['int_mode']
        Merchant.objects.filter(bus_owner_username=user).update(int_mode=i_mode)
        messages.success(request, 'Updated Successfully')
        return redirect('settings')


@login_required(login_url='login')
def w_pay(request):
    if request.method == 'POST':
        user = request.POST['user']
        w_pay_charge = request.POST['w_pay']
        Merchant.objects.filter(bus_owner_username=user).update(w_p_charges=w_pay_charge)
        messages.success(request, 'Updated Successfully')
        return redirect('settings')


def card(request):
    N = 16
    card_no = ''.join(random.choices(string.digits, k=N))
    P = 4
    pin = ''.join(random.choices(string.digits, k=P))
    c_user = request.user.username
    if request.method == 'POST':
        card_user = request.POST['username']
        if VirtualCard.objects.filter(card_user=card_user).exists():
            return redirect('dashboard')
        else:
            virtual = VirtualCard(card_user=card_user, card_no=card_no, pin=pin, card_bal='0.00')
            virtual.save()
        return redirect('dashboard')


@login_required(login_url='login')
def virtual_card(request):
    ref_no = uuid.uuid4().hex[:10].upper()
    if request.method == 'POST':
        s_username = request.POST['s_username']
        card_no = request.POST['card_no']
        amount = request.POST['amount']
        sender_bal = Account.objects.values('bal').get(username=s_username)['bal']
        card_bal = VirtualCard.objects.values('card_bal').get(card_no=card_no)['card_bal']
        status = Account.objects.values('status').get(username=s_username)['status']
        charge = Commission.objects.values('transfer').get(id=1)['transfer']
        f_charge = (float(charge))
        am = (float(amount))
        s_bal = (float(sender_bal))
        c_bal = (float(card_bal))
        c_amt = am * (f_charge / 100)
        if am > s_bal:
            messages.info(request, 'Insufficient Fund')
            return redirect('virtual_card')
        elif status == 'hold':
            messages.warning(request, 'Your Account is on Hold. Contact Admin to rectify')
            return redirect('virtual_card')
        else:
            new = (s_bal - (am + c_amt))
            Account.objects.filter(username=s_username).update(bal=new)

            new2 = c_bal + am
            VirtualCard.objects.filter(card_no=card_no).update(card_bal=new2)

            trans = Transactions(sender=s_username, receiver=card_no, amount=amount, ref_no=ref_no, description="E-Card TopUp")
            trans.save()
            messages.success(request, 'Transaction Successful')
            return redirect('virtual_card')
    return render(request, 'virtual_card.html')


@login_required(login_url='login')
def check(request):
    if request.method == 'POST':
        card_no = request.POST['card_no']
        card_check = VirtualCard.objects.filter(card_no=card_no).exists()
        if card_check:
            check = VirtualCard.objects.all().get(card_no=card_no)
            name = VirtualCard.objects.values('card_user').get(card_no=card_no)['card_user']
            first = User.objects.values('first_name').get(username=name)['first_name']
            last = User.objects.values('last_name').get(username=name)['last_name']
            cont = {'check': check, 'card_check': card_check, 'first': first, 'last': last}
            return render(request, 'virtual_card.html', cont)
        else:
            messages.error(request, 'Card Not Found')
            return redirect('virtual_card')
    return render(request, 'virtual_card.html')


@login_required(login_url='login')
def customer(request):
    c_user = request.user.id
    show = Customer.objects.filter(merchant_id=c_user)
    context = {'show': show}
    return render(request, 'customer.html', context)


@login_required(login_url='login')
def add_customer(request):
    c_user = request.user.id
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        mobile_no = request.POST['mobile_no']
        if Customer.objects.filter(email=email).exists():
            messages.error(request, 'Customer Already Exist')
            return redirect('customer')
        elif Customer.objects.filter(phone_no=mobile_no).exists():
            messages.error(request, 'Mobile Number Already Exist')
            return redirect('customer')
        else:
            cus = Customer(merchant_id=c_user, first_name=first_name, last_name=last_name, email=email,
                           phone_no=mobile_no)
            cus.save()
            messages.success(request, 'Customer Added Successfully')
            return redirect('customer')
    else:
        messages.error(request, 'Error Adding Customer')
        return redirect('customer')


@login_required(login_url='login')
def staff(request):
    c_user = request.user.id
    show = Staff.objects.filter(merchant_id=c_user)
    context = {'show': show}
    return render(request, 'staff.html', context)


@login_required(login_url='login')
def add_staff(request):
    c_user = request.user.id
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        mobile_no = request.POST['mobile_no']
        amount = request.POST['amount']
        if Staff.objects.filter(email=email).exists():
            messages.error(request, 'Staff Already Exist')
            return redirect('staff')
        elif Staff.objects.filter(phone_no=mobile_no).exists():
            messages.error(request, 'Mobile Number Already Exist')
            return redirect('staff')
        else:
            cus = Staff(merchant_id=c_user, first_name=first_name, last_name=last_name,
                        email=email, phone_no=mobile_no, amount=amount)
            cus.save()
            messages.success(request, 'Staff Added Successfully')
            return redirect('staff')
    else:
        messages.error(request, 'Error Adding Staff')
        return redirect('staff')


@login_required(login_url='login')
def upload_staff(request):
    c_user = request.user.id
    if request.method == 'POST':
        csv_file = request.FILES['file']
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'File not csv')
            return redirect('staff')

        decoded_file = csv_file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        # next(io_string)
        for data in csv.reader(io_string, delimiter=',', quotechar='|'):
            # print(data[1])
            Staff.objects.update_or_create(merchant_id=c_user,
                                           first_name=data[0],
                                           last_name=data[1],
                                           email=data[2],
                                           phone_no=data[3],
                                           amount=data[4])
        messages.success(request, 'Record Updated')
        return redirect('staff')


def delete_staff(request, id):
    Staff.objects.filter(id=id).delete()
    messages.success(request, 'Record Deleted')
    return redirect('staff')


@login_required(login_url='login')
def pay_staff(request):
    base_date_time = datetime.now()
    now = (datetime.strftime(base_date_time, "%Y-%m-%d %H:%M %p"))
    ref_no = uuid.uuid4().hex[:10].upper()
    c_user = request.user.username
    if request.method == 'POST':
        month = request.POST['month']
        comment = request.POST['comment']
        status = Account.objects.values('status').get(username=c_user)['status']
        sender = Merchant.objects.values('bus_name').get(bus_owner_username=c_user)['bus_name']
        s_bal = Account.objects.values('bal').get(username=c_user)['bal']
        am = [float(staffs.amount) for staffs in Staff.objects.all()]
        amt = (sum(am))
        sb = (float(s_bal))

        if status == 'hold':
            messages.error(request, 'Your Account is on Hold, Please contact our agent')
            return redirect('staff')
        else:
            for staffs in Staff.objects.all():
                if Account.objects.filter(phone_no=staffs.phone_no).exists():
                    bal = Account.objects.values('bal').get(phone_no=staffs.phone_no)['bal']
                    r_username = Account.objects.values('username').get(phone_no=staffs.phone_no)['username']
                    # print(am)
                    amount = Staff.objects.values('amount').get(phone_no=staffs.phone_no)['amount']
                    rb = (float(bal))
                    # print(amount)
                    new = rb + amount
                    Account.objects.filter(phone_no=staffs.phone_no).update(bal=new)

                    new2 = sb - amt
                    Account.objects.filter(username=c_user).update(bal=new2)

                    bulk = Transactions(sender=c_user, receiver=r_username, amount=staffs.amount,
                                        ref_no=ref_no, description=comment)
                    bulk.save()
                    subject, from_email, to = 'Payment', EMAIL_FROM, staffs.email
                    html_content = render_to_string('mail/email.html', {'username': r_username, 'amount': staffs.amount,
                                                                        'comment': comment, 'bal': new, 'sender': sender,
                                                                        'rb': rb, 'ref': ref_no, 'date': now})
                    text_content = strip_tags(html_content)
                    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()

                else:
                    messages.warning(request, 'Some Users info is wrong')
            messages.success(request, 'Done')
        return redirect('staff')
    else:
        messages.error(request, 'Transaction Fail')
        return redirect('staff')


def pay_single(request, id):
    base_date_time = datetime.now()
    now = (datetime.strftime(base_date_time, "%Y-%m-%d %H:%M %p"))
    ref_no = uuid.uuid4().hex[:10].upper()
    c_user = request.user.username
    r_no = Staff.objects.values('phone_no').get(id=id)['phone_no']
    # ch = Account.objects.values('phone_no').get(phone_no=r_no)['phone_no']
    if Account.objects.filter(phone_no=r_no).exists():
        amount = Staff.objects.values('amount').get(id=id)['amount']
        r_no = Staff.objects.values('phone_no').get(id=id)['phone_no']
        r_bal = Account.objects.values('bal').get(phone_no=r_no)['bal']
        s_bal = Account.objects.values('bal').get(username=c_user)['bal']
        r_email = Staff.objects.values('email').get(id=id)['email']
        s_email = User.objects.values('email').get(username=c_user)['email']
        r_username = Account.objects.values('username').get(phone_no=r_no)['username']
        r_status = Account.objects.values('status').get(phone_no=r_no)['status']
        s_status = Account.objects.values('status').get(username=c_user)['status']
        rb = (float(r_bal))
        sb = (float(s_bal))
        if amount > sb:
            messages.error(request, 'Insufficient Balance')
            return redirect('staff')
        elif r_status == 'hold':
            messages.error(request, 'User can not Recieve fun at the Moment')
            return redirect('staff')
        elif s_status == 'hold':
            messages.error(request, 'Sorry You Account is on hold')
            return redirect('staff')
        else:
            # credit Receiver
            new = rb + amount
            Account.objects.filter(phone_no=r_no).update(bal=new)

            # Debit Sender
            new2 = sb - amount
            Account.objects.filter(username=c_user).update(bal=new2)

            Transactions.objects.create(sender=c_user,
                                        receiver=r_username,
                                        amount=amount,
                                        ref_no=ref_no,
                                        description='Payment')

            # Receiver
            subject, from_email, to = 'Payment', EMAIL_FROM, r_email
            html_content = render_to_string('mail/email.html', {'username': r_username, 'amount': amount,
                                                                'comment': 'Payment', 'bal': new, 'sender': c_user,
                                                                'rb': rb, 'ref': ref_no, 'date': now})
            text_content = strip_tags(html_content)
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            # Sender
            subject, from_email, to = 'Payment', EMAIL_FROM, s_email
            html_content = render_to_string('mail/remail.html', {'username': c_user, 'amount': amount,
                                                                 'comment': 'Payment', 'bal': new2, 'sender': r_username,
                                                                 'rb': sb, 'ref': ref_no, 'date': now})
            text_content = strip_tags(html_content)
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            messages.success(request, 'Transaction Successful')
            return redirect('staff')
    else:
        messages.error(request, 'User not found')
        return redirect('staff')


@login_required(login_url='login')
def receipt(request, id):
    c_user = request.user.username
    user = Merchant.objects.all().get(bus_owner_username=c_user)
    show = Transactions.objects.all().get(id=id)
    phone = Account.objects.values('phone_no').get(username=c_user)['phone_no']
    return render(request, 'receipt.html', {'show': show, 'user_p': user, 'phone': phone})

