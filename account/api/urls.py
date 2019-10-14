from django.urls import path
from account.api.views import api_account_view, pay


app_name = 'account'

urlpatterns = [
    path('<id>/', api_account_view, name='account'),
    path('pay/<id>', pay, name='pay'),
]
