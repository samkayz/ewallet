from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User, auth
from account.models import Transactions, Account, Voucher, Ticket, Merchant, Withdraw
from .models import Resolution, Settings, Details
from django.db.models import Sum


def index(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        staff = User.objects.values('is_superuser').get(username=username)['is_superuser']
        if staff == 1:
            users = auth.authenticate(username=username, password=password)

            if users is not None:
                auth.login(request, users)
                return redirect('admin_dashboard')
            else:
                messages.info(request, 'Access Denied!!')
                return redirect('index')
        else:
            return redirect('index')
    else:
        return render(request, 'index.html')


def logout(request):
    auth.logout(request)
    return redirect('index')


def dashboard(request):
    show = Transactions.objects.aggregate(Sum('amount'))['amount__sum']
    merchant = Merchant.objects.all().count()
    users = User.objects.all().count()
    t_v = Voucher.objects.aggregate(Sum('v_amount'))['v_amount__sum']
    context = {'show': show, 'merchant': merchant, 'users': users, 't_v': t_v}
    return render(request, 'admin_dashboard.html', context)


def activity(request):
    show = Transactions.objects.filter()
    context = {'show': show}
    return render(request, 'admin_activity.html', context)


def user(request):
    show = Account.objects.filter()
    context = {'show': show}
    return render(request, 'user.html', context)


def view(request, id):
    show = Account.objects.all().get(id=id)
    username = Account.objects.values('username').get(id=id)['username']
    merchant = Merchant.objects.all().get(bus_owner_username=username)
    # print(merchant)
    context = {'show': show, 'merchant': merchant}
    return render(request, 'view.html', context)


def voucher(request):
    show = Voucher.objects.filter()
    context = {'show': show}
    return render(request, 'admin_voucher.html', context)


def dispute(request):
    show = Ticket.objects.filter()
    context = {'show': show}
    return render(request, 'admin_dispute.html', context)


def solve(request, ticket_id):
    show = Ticket.objects.all().get(ticket_id=ticket_id)
    context = {'show': show}
    return render(request, 'solve.html', context)


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
    return render(request, 'solve.html')


def page(request):
    return render(request, 'page.html')


def about(request):
    if request.method == 'POST':
        abouts = request.POST['about']

        s_about = Settings(about_us=abouts)
        s_about.save()
        messages.info(request, "Successful!!")
    return render(request, 'page.html')


def withdraw(request):
    show = Withdraw.objects.filter()
    context = {'show': show}
    return render(request, 'admin_withdraw.html', context)


def approve(request, id):
    status = Withdraw.objects.values('status').get(id=id)['status']
    if status == 'Processed':
        messages.info(request, "Payment Already Approved")
        return redirect('/super/withdraw')
    else:
        Withdraw.objects.filter(id=id).update(status='Processed')
        messages.info(request, "Payment Approved Successfully!")
        return redirect('/super/withdraw')


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
