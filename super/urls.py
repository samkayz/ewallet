from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('index', views.index, name='index'),
    path('dashboard', views.dashboard, name='admin_dashboard'),
    path('activity', views.activity, name='admin_activity'),
    path('logout', views.logout, name='logout'),
    path('user', views.user, name='user'),
    path('view/<id>', views.view, name='view'),
    path('voucher', views.voucher, name='admin_voucher'),
    path('dispute', views.dispute, name='admin_dispute'),
    path('solve/<ticket_id>', views.solve, name='solve'),
    path('resolution', views.resolution, name='resolution'),
]
