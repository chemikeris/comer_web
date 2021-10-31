from django.shortcuts import render
from django.conf import settings

def index(request):
    return render(request, 'site/index.html')

def help(request):
    return render(request, 'site/help.html')

def api_help(request):
    context = {}
    available_databases = {}
    def nice_db_names(desc_tuples):
        dbs = []
        for desc_tuple in desc_tuples:
            computer_db_name, human_db_name = desc_tuple
            db_name = '%s (%s)' % (human_db_name, computer_db_name)
            dbs.append(db_name)
        return ', '.join(dbs)
    available_databases['COMER'] = nice_db_names(settings.COMER_DATABASES)
    available_databases['COTHER'] = nice_db_names(settings.COTHER_DATABASES)
    available_databases['HHsuite'] = nice_db_names(settings.HHSUITE_DATABASES)
    available_databases['HMMER'] = nice_db_names(settings.SEQUENCE_DATABASES)
    context['db'] = available_databases
    return render(request, 'site/api_help.html', context)

def availability(request):
    return render(request, 'site/availability.html')

def references(request):
    return render(request, 'site/references.html')

