from django.urls import path
from . import views


urlpatterns = [
    path('', views.pay, name='pay'),
    path('initiate', views.initiate, name='initiate'),
    path('error', views.error, name='error'),
    path('success', views.success, name='success'),
    path('logout', views.logout, name='logout'),
]
