from django.shortcuts import render, redirect

from apps.core.models import get_databases_for

def index(request):
    return redirect('input')

def help(request):
    page_title = 'COMER web server help'
    return render(request, 'site/help.html', {'page_title': page_title})

def api_help(request):
    context = {}
    available_databases = {}
    def nice(desc_tuples):
        dbs = []
        for desc_tuple in desc_tuples:
            computer_db_name, human_db_name = desc_tuple
            db_name = '%s (%s)' % (
                computer_db_name, human_db_name.split('_')[0]
                )
            dbs.append(db_name)
        return ', '.join(dbs)
    available_databases['COMER'] = nice(get_databases_for('comer'))
    # available_databases['COTHER'] = nice(get_databases_for('cother'))
    available_databases['HHsuite'] = nice(get_databases_for('hhsuite'))
    available_databases['HMMER'] = nice(get_databases_for('hmmer'))
    short_db_names = {}
    short_db_names['COMER'] = [
        d[0] for d in get_databases_for('comer', ['pdb', 'pfam', 'swissprot'])
        ]
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


# GTalign server functions
def gtalign_help(request):
    context = {}
    context['page_title'] = 'GTalign web server help'
    return render(request, 'site/gtalign_help.html', context)

def gtalign_tutorial(request):
    pass

def gtalign_about(request):
    pass

