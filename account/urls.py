from django.urls import path
from . import views

urlpatterns = [
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('register', views.register, name='register'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('transfer', views.transfer, name='transfer'),
    path('verify', views.verify, name='verify'),
    path('settings', views.settings, name='settings'),
    path('activity', views.activity, name='activity'),
    path('voucher', views.voucher, name='voucher'),
    path('load_voucher', views.load_voucher, name='load_voucher'),
    path('ticket', views.ticket, name='ticket'),
    path('dispute', views.dispute, name='dispute'),
    path('merchant', views.merchant, name='merchant'),
    path('api', views.api, name='api'),
    path('reply/<ticket_id>', views.reply, name='reply'),
    path('resolution', views.resolution, name='resolution'),
    path('bank', views.bank, name='bank'),
    path('withdraw', views.withdraw, name='withdraw'),
    path('deposit', views.deposit, name='deposit'),
    path('confirm', views.confirm, name='confirm'),
    path('payment', views.payment, name='payment'),

]
