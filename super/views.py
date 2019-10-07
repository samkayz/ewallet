from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User, auth
from account.models import Transactions, Account


def index(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        staff = User.objects.values('is_superuser').get(username=username)['is_superuser']
        user = auth.authenticate(username=username, password=password)

        if user is not None and staff == 1:
            auth.login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.info(request, 'Access Denied!!')
            return redirect('index')
    else:
        return render(request, 'index.html')


def logout(request):
    auth.logout(request)
    return redirect('index')


def dashboard(request):
    return render(request, 'admin_dashboard.html')


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
    context = {'show': show}
    return render(request, 'view.html', context)
