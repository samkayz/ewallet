from django.shortcuts import render
from super.models import Details


def landing(request):
    show = Details.objects.all().get(id=1)
    context = {'show': show}
    return render(request, 'landing.html', context)


def about(request):
    show = Details.objects.all().get(id=1)
    context = {'show': show}
    return render(request, 'about.html', context)


def pricing(request):
    show = Details.objects.all().get(id=1)
    context = {'show': show}
    return render(request, 'pricing.html', context)


def contact(request):
    show = Details.objects.all().get(id=1)
    context = {'show': show}
    return render(request, 'contact.html', context)
