from django.shortcuts import render, redirect
from django.conf import settings

def index(request):
    return redirect('input')

def help(request):
    page_title = 'COMER web server help'
    return render(request, 'site/help.html', {'page_title': page_title})

def api_help(request):
    context = {}
    available_databases = {}
    def nice_db_names(desc_tuples):
        dbs = []
        for desc_tuple in desc_tuples:
            computer_db_name, human_db_name = desc_tuple
            db_name = '%s (%s)' % (
                computer_db_name, human_db_name.split('_')[0]
                )
            dbs.append(db_name)
        return ', '.join(dbs)
    available_databases['COMER'] = nice_db_names(settings.COMER_DATABASES)
    available_databases['COTHER'] = nice_db_names(settings.COTHER_DATABASES)
    available_databases['HHsuite'] = nice_db_names(settings.HHSUITE_DATABASES)
    available_databases['HMMER'] = nice_db_names(settings.SEQUENCE_DATABASES)
    short_db_names = {}
    short_db_names['COMER'] = [d[0] for d in settings.COMER_DATABASES]
    short_db_names['COTHER'] = [d[0] for d in settings.COTHER_DATABASES]
    short_db_names['HHsuite'] = [d[0] for d in settings.HHSUITE_DATABASES]
    short_db_names['HMMSR'] = [d[0] for d in settings.SEQUENCE_DATABASES]
    context['db'] = available_databases
    context['short_db_names'] = short_db_names
    context['page_title'] = 'COMER web server API help'
    return render(request, 'site/api_help.html', context)

def tutorial(request):
    page_title = 'COMER web server tutorial'
    return render(request, 'site/tutorial.html', {'page_title': page_title})

def about(request):
    page_title = 'COMER web server'
    return render(request, 'site/about.html', {'page_title': page_title})

