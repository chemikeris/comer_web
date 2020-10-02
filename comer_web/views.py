from django.shortcuts import render

def index(request):
    return render(request, 'site/index.html')

def help(request):
    return render(request, 'site/help.html')
