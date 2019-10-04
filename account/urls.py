from django.urls import path
from . import views

urlpatterns = [
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('register', views.register, name='register'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('transfer', views.transfer, name='transfer'),
    path('verify', views.verify, name='verify'),
    path('profile', views.profile, name='profile'),
    path('activity', views.activity, name='activity'),
    path('voucher', views.voucher, name='voucher'),
    path('load_voucher', views.load_voucher, name='load_voucher'),

]
