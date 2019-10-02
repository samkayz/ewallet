from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User, auth
from .models import Account
import random
import string
import uuid


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
    c_user = request.user.username
    show = Account.objects.all().get(username=c_user)
    context = {'show': show}
    return render(request, 'transfer.html', context)


def verify(request):
    if request.method == 'POST':
        r_number = request.POST['number']
        check = Account.objects.all().get(phone_no=r_number)
        context = {'check': check}
    return render(request, 'transfer.html', context)
