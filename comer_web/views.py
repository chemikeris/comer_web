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
        return '; '.join(dbs)
    available_databases['COMER'] = settings.COMER_DATABASES
    available_databases['COTHER'] = settings.COTHER_DATABASES
    available_databases['HHsuite'] = settings.HHSUITE_DATABASES
    available_databases['HMMER'] = settings.SEQUENCE_DATABASES
    context['db'] = available_databases
    return render(request, 'site/api_help.html', context)

