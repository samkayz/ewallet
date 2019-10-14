"""wallet URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from .import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('index', views.landing, name='landing'),
    path('about', views.about, name='about'),
    path('pricing', views.pricing, name='pricing'),
    path('contact', views.contact, name='contact'),
    path('super/', include('super.urls')),
    path('account/', include('account.urls')),
    path('api/', include('account.api.urls', 'api')),
    path('pay/', include('pay.urls')),
]
