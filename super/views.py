from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from account.models import Transactions, Account, Voucher, Ticket, Merchant, Withdraw
from .models import Resolution, Settings, Details
from django.db.models import Sum
import uuid


def index(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        staff = User.objects.values('is_superuser').get(username=username)['is_superuser']
        if staff == 1:
            users = auth.authenticate(username=username, password=password)

            if users is not None:
                auth.login(request, users)
                return redirect('home')
            else:
                messages.info(request, 'Access Denied!!')
                return redirect('index')
        else:
            return redirect('index')
    else:
        return render(request, 'admin/index.html')


def logout(request):
    auth.logout(request)
    return redirect('index')


@login_required(login_url='index')
def home(request):
    show = Transactions.objects.aggregate(Sum('amount'))['amount__sum']
    merchant = Merchant.objects.all().count()
    users = User.objects.all().count()
    ticket = Ticket.objects.filter()
    vendor = Merchant.objects.filter()
    t_v = Voucher.objects.aggregate(Sum('v_amount'))['v_amount__sum']
    context = {'show': show, 'merchant': merchant, 'users': users, 't_v': t_v, 'ticket': ticket, 'vendor': vendor}
    return render(request, 'admin/home.html', context)


@login_required(login_url='index')
def activity(request):
    show = Transactions.objects.filter()
    context = {'show': show}
    return render(request, 'admin/activity.html', context)


@login_required(login_url='index')
def user(request):
    show = Account.objects.filter()
    context = {'show': show}
    return render(request, 'admin/user.html', context)


@login_required(login_url='index')
def view(request, id):
    show = Account.objects.all().get(id=id)
    username = Account.objects.values('username').get(id=id)['username']
    if Merchant.objects.filter(bus_owner_username=username).exists():
        merchant = Merchant.objects.all().get(bus_owner_username=username)
        context = {'show': show, 'merchant': merchant}
        return render(request, 'admin/view.html', context)
    else:
        context = {'show': show}
        return render(request, 'admin/view.html', context)


@login_required(login_url='index')
def voucher(request):
    show = Voucher.objects.filter()
    context = {'show': show}
    return render(request, 'admin/voucher.html', context)


@login_required(login_url='index')
def dispute(request):
    show = Ticket.objects.filter()
    context = {'show': show}
    return render(request, 'admin/dispute.html', context)


@login_required(login_url='index')
def solve(request, ticket_id):
    show = Resolution.objects.filter(Q(ticket_id=ticket_id))
    context = {'show': show}
    return render(request, 'admin/solve.html', context)


@login_required(login_url='index')
def resolution(request):
    if request.method == 'POST':
        ticket_id = request.POST['ticket_id']
        subject = request.POST['subject']
        category = request.POST['category']
        content = request.POST['content']
        ticket_status = request.POST['ticket_status']

        Ticket.objects.filter(ticket_id=ticket_id).update(status=ticket_status)
        t_save = Resolution(ticket_id=ticket_id, subject=subject, category=category, content=content)
        t_save.save()
        messages.info(request, "Successful!!")
    return render(request, 'admin/solve.html')


@login_required(login_url='index')
def page(request):
    return render(request, 'admin/page.html')


@login_required(login_url='index')
def verify(request):
    if request.method == 'POST':
        r_number = request.POST['number']
        if Account.objects.filter(phone_no=r_number).exists():
            check = Account.objects.all().get(phone_no=r_number)
            cont = {'check': check}
            return render(request, 'admin/send.html', cont)
        else:
            messages.info(request, 'Mobile Number Not Found')
            return redirect('send')

    return render(request, 'admin/send.html')


@login_required(login_url='index')
def send(request):
    ref_no = uuid.uuid4().hex[:10].upper()
    if request.method == 'POST':
        r_number = request.POST['r_number']
        amount = request.POST['amount']
        bal = Account.objects.values('bal').get(phone_no=r_number)['bal']
        show = Account.objects.values().get(phone_no=r_number)['username']
        # print("Hello: ", show)
        rb = (float(bal))
        am = (float(amount))
        if am <= 0:
            messages.info(request, 'Invalid Transaction')
            return redirect('send')
        else:
            new = rb + am
            Account.objects.filter(phone_no=r_number).update(bal=new)
            trans = Transactions(sender='System', receiver=show, amount=amount, ref_no=ref_no, )
            trans.save()
            messages.info(request, "Transaction Successful!!")
    return render(request, 'admin/send.html')


@login_required(login_url='index')
def about(request):
    if request.method == 'POST':
        abouts = request.POST['about']

        s_about = Settings(about_us=abouts)
        s_about.save()
        messages.info(request, "Successful!!")
    return render(request, 'admin/page.html')


@login_required(login_url='index')
def withdraw(request):
    show = Withdraw.objects.filter()
    context = {'show': show}
    return render(request, 'admin/withdraw.html', context)


@login_required(login_url='index')
def approve(request, id):
    status = Withdraw.objects.values('status').get(id=id)['status']
    if status == 'Processed':
        messages.info(request, "Payment Already Approved")
        return redirect('/super/withdraw')
    else:
        Withdraw.objects.filter(id=id).update(status='Processed')
        messages.info(request, "Payment Approved Successfully!")
        return redirect('/super/withdraw')


@login_required(login_url='index')
def details(request):
    if request.method == 'POST':
        address = request.POST['address']
        email = request.POST['email']
        phone_no = request.POST['number']
        fax = request.POST['fax']

        if Details.objects.all().count() >= 1:
            Details.objects.filter(id=1).update(address=address, email=email, phone_no=phone_no, fax=fax)
            messages.info(request, 'Information Updated')
            return redirect('details')
        else:
            d_detail = Details(address=address, email=email, phone_no=phone_no, fax=fax)
            d_detail.save()
            messages.info(request, 'Successful')
            return redirect('details')
    show = Details.objects.all().get(id=1)
    context = {'show': show}
    return render(request, 'details.html', context)


@login_required(login_url='index')
def contact(request):
    if request.method == 'POST':
        email = request.POST['email']
        phone_no = request.POST['phone_no']
        address = request.POST['address']
        if Settings.objects.filter(id=1).exists():
            Settings.objects.filter(id=1).update(address=address, phone_no=phone_no, email=email)
            messages.info(request, 'Successful')
            return redirect('contact')
        else:
            s_save = Settings(address=address, phone_no=phone_no, email=email,)
            s_save.save()
            messages.info(request, 'Successful')
            return redirect('contact')
    show = Settings.objects.all().get(id=1)
    context = {'show': show}
    return render(request, 'admin/contact.html', context)


def payment_api(request):
    if request.method == 'POST':
        paystack = request.POST['paystack']
        if Settings.objects.filter(Q(id=1)).exists():
            Settings.objects.filter(Q(id=1)).update(paystack_api=paystack)
            messages.info(request, 'Added Successfully')
            return redirect('payment-api')
        else:
            s_pay = Settings(paystack_api=paystack)
            s_pay.save()
            messages.info(request, 'Added Successfully')
            return redirect('payment-api')
    show = Settings.objects.all().get(id=1)
    context = {'show': show}
    return render(request, 'admin/payment_api.html', context)


@login_required(login_url='index')
def v_verify(request):
    if request.method == 'POST':
        r_number = request.POST['number']
        if Account.objects.filter(phone_no=r_number).exists():
            check = Account.objects.all().get(phone_no=r_number)
            cont = {'check': check}
            return render(request, 'admin/solve_voucher.html', cont)
        else:
            messages.info(request, 'Mobile Number Not Found')
            return redirect('v_verify')

    return render(request, 'admin/solve_voucher.html')


@login_required(login_url='index')
def voucher_issue(request):
    ref_no = uuid.uuid4().hex[:10].upper()
    if request.method == 'POST':
        r_number = request.POST['r_number']
        v_code = request.POST['v_code']
        status = Voucher.objects.values('v_status').get(v_code=v_code)['v_status']
        if Voucher.objects.filter(v_code=v_code).exists():
            if status == 'open':
                amount = Voucher.objects.values('v_amount').get(v_code=v_code)['v_amount']
                bal = Account.objects.values('bal').get(phone_no=r_number)['bal']
                am = (float(amount))
                r_bal = (float(bal))
                new = am + r_bal
                Account.objects.filter(phone_no=r_number).update(bal=new)
                Voucher.objects.filter(v_code=v_code).update(v_status='close')
                trans = Transactions(sender='System', receiver=r_number, amount=amount, ref_no=ref_no, )
                trans.save()
                messages.info(request, "Transaction Successful!!")
                return render(request, 'admin/solve_voucher.html')
            else:
                messages.info(request, "Voucher Used")
                return redirect('solve-voucher')
        else:
            messages.info(request, "Voucher Not Found")
            return redirect('solve-voucher')

    return render(request, 'admin/solve_voucher.html')


@login_required(login_url='index')
def lock(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        users = auth.authenticate(username=username, password=password)
        if users is not None:
            auth.login(request, users)
            return redirect('home')
        else:
            messages.info(request, 'Access Denied!!')
            return redirect('lock')
    return render(request, 'admin/lock.html')


def hold(request, id):
    Account.objects.filter(id=id).update(status="hold")
    return redirect('user')


def un_hold(request, id):
    Account.objects.filter(id=id).update(status="unhold")
    return redirect('user')
