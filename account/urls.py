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
    path('compose', views.compose, name='create-ticket'),
    path('dispute', views.dispute, name='dispute'),
    path('merchant', views.merchant, name='merchant'),
    path('api', views.api, name='api'),
    path('reply/<ticket_id>', views.reply, name='reply'),
    path('resolution', views.resolution, name='resolution'),
    path('bank', views.bank, name='bank'),
    path('delete/<id>', views.delete, name='delete'),
    path('withdraw', views.withdraw, name='withdraw'),
    path('deposit', views.deposit, name='deposit'),
    path('confirm', views.confirm, name='confirm'),
    path('payment', views.payment, name='payment'),
    path('invoice', views.invoice, name='invoice'),
    path('invoice_verify', views.invoice_verify, name='verify'),
    path('pay_invoice', views.pay_invoice, name='pay-invoice'),
    path('success/<id>', views.success, name='success'),
    path('reject/<id>', views.reject, name='reject'),
    path('paid_invoice', views.paid_invoice, name='paid-invoice'),
    path('load', views.load, name='load'),
    path('payment', views.payment, name='payment'),
    path('fail', views.fail, name='fail'),
    path('int_mode', views.int_mode, name='mode'),
    path('w_pay', views.w_pay, name='who-pay-charges'),

]
