from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from .models import Account, Transactions, Voucher, Ticket, Merchant, Bank, Withdraw
from super.models import Resolution
import random
import string
import uuid
import datetime


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('dashboard')
        else:
            messages.info(request, 'Invalid Credentials')
            return redirect('login')
    else:
        return render(request, 'login.html')


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
                messages.info(request, 'Username taken')
                return redirect('register')
            elif User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
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
                                bal='0',)
            users.save()
            user.save()
            messages.info(request, 'Account Created Successfully')
            return redirect('register')
        else:
            messages.info(request, 'Password not Matching')
            return redirect('register')

    else:
        return render(request, 'register.html')


@login_required(login_url='login')
def dashboard(request):
    c_user = request.user.username
    show = Account.objects.all().get(username=c_user)
    context = {'show': show}
    return render(request, 'dashboard.html', context)


def logout(request):
    auth.logout(request)
    return redirect('login')


@login_required(login_url='login')
def transfer(request):
    ref_no = uuid.uuid4().hex[:10].upper()
    if request.method == 'POST':
        s_username = request.POST['s_username']
        r_number = request.POST['r_number']
        amount = request.POST['amount']
        bal = Account.objects.values('bal').get(phone_no=r_number)['bal']
        s_bal = Account.objects.values('bal').get(username=s_username)['bal']
        show = Account.objects.values().get(phone_no=r_number)['username']
        # print("Hello: ", show)
        sb = (float(s_bal))
        rb = (float(bal))
        am = (float(amount))

        if am > sb:
            messages.info(request, 'Insufficient Balance')
        elif s_username == show:
            messages.info(request, "You Can't Send Money to Yourself!!")
        else:
            new = rb + am
            Account.objects.filter(phone_no=r_number).update(bal=new)

            new_2 = sb - am
            Account.objects.filter(username=s_username).update(bal=new_2)

            trans = Transactions(sender=s_username,
                                 receiver=show,
                                 amount=amount,
                                 ref_no=ref_no,)
            trans.save()
            messages.info(request, "Transaction Successful!!")
    return render(request, 'transfer.html')


@login_required(login_url='login')
def verify(request):
    if request.method == 'POST':
        r_number = request.POST['number']
        if Account.objects.filter(phone_no=r_number).exists():
            check = Account.objects.all().get(phone_no=r_number)
            cont = {'check': check}
            return render(request, 'transfer.html', cont)
        else:
            messages.info(request, 'Mobile Number Not Found')
            return redirect('transfer')

    return render(request, 'transfer.html')


@login_required(login_url='login')
def settings(request):
    c_user = request.user.username
    if Merchant.objects.filter(bus_owner_username=c_user).exists():
        s_show = Merchant.objects.all().get(bus_owner_username=c_user)
        show = Account.objects.values('phone_no').get(username=c_user)['phone_no']
        cus_id = Account.objects.values('customer_id').get(username=c_user)['customer_id']
        context = {'s_show': s_show, 'show': show, 'cus_id': cus_id}
        return render(request, 'settings.html', context)
    else:
        return redirect('api')


@login_required(login_url='login')
def activity(request):
    c_user = request.user.username
    show = Transactions.objects.filter(Q(sender=c_user) | Q(receiver=c_user))
    # print("Hello:", show)
    context = {'show': show}
    return render(request, 'activity.html', context)


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
        sb = (float(s_bal))
        am = (float(amount))
        if am > sb:
            messages.info(request, 'Insufficient Balance')
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
                                 ref_no=ref_no, )
            trans.save()
            v_save.save()
            messages.info(request, "Transaction Successful!!")
    show = Voucher.objects.filter(Q(v_creator=c_user))
    context = {'show': show}
    return render(request, 'voucher.html', context)


@login_required(login_url='login')
def load_voucher(request):
    ref_no = uuid.uuid4().hex[:10].upper()
    now = datetime.datetime.now()
    c_user = request.user.username
    if request.method == 'POST':
        v_code = request.POST['v_code']
        l_username = request.POST['l_username']
        if Voucher.objects.filter(v_code=v_code).exists():
            v_am = Voucher.objects.values('v_amount').get(v_code=v_code)['v_amount']
            status = Voucher.objects.values('v_status').get(v_code=v_code)['v_status']
            loader = Voucher.objects.values('v_creator').get(v_code=v_code)['v_creator']
            bal = Account.objects.values('bal').get(username=c_user)['bal']
            sb = (float(bal))
            am = (float(v_am))

            if status == 'close':
                messages.info(request, "Voucher Used")
                return redirect('load_voucher')
            elif loader == l_username:
                messages.info(request, "You Cant load the Voucher you Created")
                return redirect('load_voucher')
            else:
                new = sb + am
                Account.objects.filter(username=l_username).update(bal=new)
                Voucher.objects.filter(v_code=v_code).update(v_status='close', v_loader=c_user, v_date_load=now)
                messages.info(request, "Transaction Successful!!")

                trans = Transactions(sender='Voucher', receiver=l_username, amount=am, ref_no=ref_no,)
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
    return render(request, 'ticket.html')


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

        if Merchant.objects.filter(bus_owner_username=c_user).exists():
            messages.info(request, "You are a Merchant Already")
            return redirect('settings')

        else:
            b_save = Merchant(bus_owner_username=c_user, bus_name=b_name, bus_address=b_address, bus_email=b_email,
                              bus_no=b_tel, bus_website=b_url,)
            b_save.save()
            messages.info(request, "Merchant Registration Successful")
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

        Merchant.objects.filter(bus_owner_username=user).update(api_test_key=api_test, api_live_key=api_live)
        messages.info(request, "Please Find Your API key on API Tab")
        return redirect('settings')
    show = Account.objects.values('phone_no').get(username=c_user)['phone_no']
    cus_id = Account.objects.values('customer_id').get(username=c_user)['customer_id']
    context = {'show': show, 'cus_id': cus_id}
    return render(request, 'settings.html', context)


@login_required(login_url='login')
def reply(request, ticket_id):
    show = Ticket.objects.all().get(ticket_id=ticket_id)
    r_show = Resolution.objects.filter(Q(ticket_id=ticket_id))
    context = {'show': show, 'r_show': r_show}
    return render(request, 'reply.html', context)


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
        return redirect('dispute')
    return render(request, 'reply.html')


@login_required(login_url='login')
def bank(request):
    c_user = request.user.username
    if request.method == 'POST':
        acct_name = request.POST['acct_name']
        acct_no = request.POST['acct_no']
        bank_name = request.POST['bank_name']

        s_bank = Bank(username=c_user, account_name=acct_name, account_no=acct_no, bank_name=bank_name)
        s_bank.save()
        messages.info(request, "Added Successful!!")
        return redirect('settings')
    return render(request, 'settings.html')


@login_required(login_url='login')
def withdraw(request):
    ref_no = uuid.uuid4().hex[:10].upper()
    c_user = request.user.username
    if request.method == 'POST':
        acct_no = request.POST['bank_name']
        amount = request.POST['amount']
        acct_name = Bank.objects.values('account_name').get(account_no=acct_no)['account_name']
        bank_name = Bank.objects.values('bank_name').get(account_no=acct_no)['bank_name']
        bal = Account.objects.values('bal').get(username=c_user)['bal']
        sb = (float(bal))
        am = (float(amount))
        if am <= 0:
            messages.info(request, 'Invalid Transaction')
            return redirect('withdraw')
        elif sb < am:
            messages.info(request, 'Low Balance ')
            return redirect('withdraw')
        elif am < 1000.0:
            messages.info(request, 'Withdraw Minimum is 1,000 ')
            return redirect('withdraw')
        else:
            new = sb-am
            Account.objects.filter(username=c_user).update(bal=new)
            s_withdraw = Withdraw(username=c_user, amount=amount, acct_name=acct_name, acct_no=acct_no,
                                  bank_name=bank_name, status='pending', ref_no=ref_no,)
            trans = Transactions(sender=c_user,
                                 receiver='Withdrawal',
                                 amount=amount,
                                 ref_no=ref_no, )
            trans.save()
            s_withdraw.save()
            messages.info(request, "Successful!!")
    show = Bank.objects.filter(Q(username=c_user))
    u_withdraw = Withdraw.objects.filter(Q(username=c_user))
    context = {'show': show, 'u_withdraw': u_withdraw}
    return render(request, 'withdraw.html', context)


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


def confirm(request):
    return render(request, 'confirm.html')


def payment(request):
    username = request.session['username']
    amount = request.session['amount']
    ref_no = request.session['ref_no']
    bal = Account.objects.values('bal').get(username=username)['bal']
    sb = (float(bal))
    am = (float(amount))
    new = sb + am
    Account.objects.filter(username=username).update(bal=new)
    messages.info(request, 'Transaction Successful')
    trans = Transactions(sender='Card Payment', receiver=username, amount=am, ref_no=ref_no, )
    trans.save()
    return render(request, 'deposit.html')
