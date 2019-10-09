from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User, auth
from .models import Account, Transactions, Voucher, Ticket, Merchant
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


def dashboard(request):
    c_user = request.user.username
    show = Account.objects.all().get(username=c_user)
    context = {'show': show}
    return render(request, 'dashboard.html', context)


def logout(request):
    auth.logout(request)
    return redirect('login')


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


def settings(request):
    c_user = request.user.username
    show = Account.objects.all().get(username=c_user)
    s_show = Merchant.objects.all().get(bus_owner_username=c_user)
    m_show = Merchant.objects.all().get(bus_owner_username=c_user)
    context = {'show': show, 's_show': s_show, 'm_show': m_show}
    return render(request, 'settings.html', context)


def activity(request):
    c_user = request.user.username
    show = Transactions.objects.filter(Q(sender=c_user) | Q(receiver=c_user))
    # print("Hello:", show)
    context = {'show': show}
    return render(request, 'activity.html', context)


def voucher(request):
    N = 10
    code = ''.join(random.choices(string.digits, k=N))
    ref_no = uuid.uuid4().hex[:10].upper()
    c_user = request.user.username
    if request.method == 'POST':
        v_username = request.POST['v_username']
        amount = request.POST['amount']
        s_bal = Account.objects.values('bal').get(username=v_username)['bal']
        sb = (float(s_bal))
        am = (float(amount))
        if am > sb:
            messages.info(request, 'Insufficient Balance')
        else:
            new_2 = sb - am
            Account.objects.filter(username=v_username).update(bal=new_2)
            v_save = Voucher(v_creator=v_username,
                             v_code=code,
                             v_amount=am,
                             ref_no=ref_no,
                             v_status='open',
                             )
            trans = Transactions(sender=v_username,
                                 receiver='voucher',
                                 amount=amount,
                                 ref_no=ref_no, )
            trans.save()
            v_save.save()
            messages.info(request, "Transaction Successful!!")
    show = Voucher.objects.filter(Q(v_creator=c_user))
    context = {'show': show}
    return render(request, 'voucher.html', context)


def load_voucher(request):
    ref_no = uuid.uuid4().hex[:10].upper()
    now = datetime.datetime.now()
    c_user = request.user.username
    if request.method == 'POST':
        v_code = request.POST['v_code']
        l_username = request.POST['l_username']
        ju = Voucher.objects.filter(v_code=v_code)
        get_object_or_404(ju, v_code=v_code)
        v_am = Voucher.objects.values('v_amount').get(v_code=v_code)['v_amount']
        status = Voucher.objects.values('v_status').get(v_code=v_code)['v_status']
        loader = Voucher.objects.values('v_creator').get(v_code=v_code)['v_creator']
        bal = Account.objects.values('bal').get(username=c_user)['bal']
        sb = (float(bal))
        am = (float(v_am))

        if status == 'close':
            messages.info(request, "Voucher Used")
        elif loader == l_username:
            messages.info(request, "You Cant load the Voucher you Created")
        else:
            new = sb + am
            Account.objects.filter(username=l_username).update(bal=new)
            Voucher.objects.filter(v_code=v_code).update(v_status='close', v_loader=c_user, v_date_load=now)
            messages.info(request, "Transaction Successful!!")

            trans = Transactions(sender='Voucher', receiver=l_username, amount=am, ref_no=ref_no,)
            trans.save()
    show = Voucher.objects.filter(Q(v_creator=c_user))
    context = {'show': show}
    return render(request, 'load_voucher.html', context)


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


def dispute(request):
    c_user = request.user.username
    show = Ticket.objects.filter(Q(owner=c_user))
    context = {'show': show}
    return render(request, 'dispute.html', context)


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
    return render(request, 'settings.html')


def api(request):
    api_test = uuid.uuid4().hex[:50].lower()
    api_live = uuid.uuid4().hex[:50].lower()
    if request.method == 'POST':
        user = request.POST['user']

        Merchant.objects.filter(bus_owner_username=user).update(api_test_key=api_test, api_live_key=api_live)
        messages.info(request, "Please Find Your API key on API Tab")
        return redirect('settings')
    return render(request, 'settings.html')


def reply(request, ticket_id):
    show = Ticket.objects.all().get(ticket_id=ticket_id)
    r_show = Resolution.objects.filter(Q(ticket_id=ticket_id))
    context = {'show': show, 'r_show': r_show}
    return render(request, 'reply.html', context)


