from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('index', views.index, name='index'),
    path('home', views.home, name='home'),
    path('activity', views.activity, name='admin_activity'),
    path('logout', views.logout, name='logout'),
    path('user', views.user, name='user'),
    path('view/<id>', views.view, name='view'),
    path('send', views.send, name='send'),
    path('verify', views.verify, name='verify'),
    path('v_verify', views.v_verify, name='v_verify'),
    path('voucher', views.voucher, name='admin_voucher'),
    path('dispute', views.dispute, name='admin_dispute'),
    path('solve/<ticket_id>', views.solve, name='solve'),
    path('resolution', views.resolution, name='resolution'),
    path('page', views.page, name='page'),
    path('about', views.about, name='about'),
    path('withdraw', views.withdraw, name='withdraw'),
    path('approve/<id>', views.approve, name='approve'),
    path('details', views.details, name='details'),
    path('contact', views.contact, name='contact'),
    path('solve_voucher', views.voucher_issue, name='solve-voucher'),
    path('lock', views.lock, name='lock'),
    path('payment-api', views.payment_api, name='payment-api'),
    path('hold/<id>', views.hold, name='hold'),
    path('un_hold/<id>', views.un_hold, name='unhold'),
]
