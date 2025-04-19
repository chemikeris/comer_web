import os
import copy

from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse, JsonResponse, FileResponse, \
        QueryDict
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.utils.safestring import mark_safe

from . import default
from . import models
from apps.core import utils
from apps.core.models import get_databases_for
from apps.core.sequences import read_example_queries
from apps.website.models import set_and_get_session_jobs


def input(request):
    "View to input query sequences or MSA"
    from .forms import SequencesInputForm
    InputForm = SequencesInputForm

    if request.method == 'POST':
        form = InputForm(request.POST, request.FILES)
        if form.is_valid():
            new_job = models.process_input_data(
                form.cleaned_data, request.FILES
                )
            return redirect('results', job_id=new_job.name)
    else:
        search_settings = copy.deepcopy(default.search_settings)
        form = InputForm(initial=search_settings)
    context = {
        'form': form, 'example_str': mark_safe(read_example_queries()),
        'recent_jobs': set_and_get_session_jobs(request),
        'page_title': 'COMER web server'
        }
    return render(request, 'search/input.html', context)


@csrf_exempt
def submit(request):
    "Submit query input from command line"
    if request.method == 'POST':
        # Generating starting data based on default search settings.
        input_data_and_settings = QueryDict(mutable=True)
        input_data_and_settings.update(copy.deepcopy(default.search_settings))
        # If there are input data in POST request, changing the defaults to
        # user selected parameters.
        input_data_and_settings.update(request.POST)
        # Filling default databases, if they are not provided by user.
        input_data_and_settings.setdefault(
            'number_of_results', default.number_of_results
            )
        input_data_and_settings.setdefault(
            'comer_db', get_databases_for('comer', ['pdb'])[0][0]
            )
        input_data_and_settings.setdefault(
            'cother_db', get_databases_for('cother', ['pdb'])[0][0]
            )
        input_data_and_settings.setdefault(
            'hhsuite_db', get_databases_for('hhsuite')[0][0]
            )
        input_data_and_settings.setdefault(
            'sequence_db', get_databases_for('hmmer')[0][0]
            )
        from .forms import SequencesInputFormWithAllSettings
        form = SequencesInputFormWithAllSettings(
            input_data_and_settings, request.FILES
            )
        result = {}
        if form.is_valid():
            new_job = models.process_input_data(
                form.cleaned_data, request.FILES
                )
            result['success'] = True
            result['job_id'] = new_job.name
        else:
            result['success'] = False
            result['form_errors'] = dict(form.errors.items())
    else:
        result = {}
    return JsonResponse(result)


class ApiResultsView(View):
    "Parent class for API views"
    def get(self, request, job_id, sequence_no=None):
        job_exists = models.Job.objects.filter(name=job_id)
        if job_exists:
            job = job_exists[0]
            result_response = self.format_output(job, sequence_no)
        else:
            result = {}
            result['success'] = False
            result['status'] = 'Job %s does not exist!' % job_id
            result_response = JsonResponse(result)
        return result_response

    def start_output_for_successful_result(self, job):
        result = {}
        result['success'] = True
        finished, removed, status_msg, errors, refresh = job.status_info()
        result['job_id'] = job.name
        result['status'] = status_msg
        result['search_method'] = 'COTHER' if job.is_cother_search else 'COMER'
        result['error_log'] = '' if errors is None else errors
        return result

    def format_output(self, *args, **kwargs):
        raise NotImplementedError


class ApiJobStatus(ApiResultsView):
    "API view showing job status"
    def format_output(self, job, sequence_no=None):
        result = self.start_output_for_successful_result(job)
        del result['error_log']
        result['log'] = job.calculation_log
        return JsonResponse(result)


def results(request, job_id, redirect_to_first=False):
    job = get_object_or_404(models.Job, name=job_id)
    print(job)
    finished, removed, status_msg, errors, refresh = job.status_info()
    page_title = '%s results - %s' % (job.method().upper(), job.nice_name())
    if finished and not removed:
        if job.number_of_input_queries == 1 and redirect_to_first:
            print('Single-sequence job, redirecting.')
            return redirect('detailed', job_id=job_id, result_no=0)

        summary = job.results_summary()
        sequences = [r.input_name for r in summary]
        context = {
            'job': job,
            'page_title': page_title,
            'recent_jobs': set_and_get_session_jobs(request, job),
            'structure_models': [],
            'generated_msas': [],
            'sequences': sequences,
            'sequence_no': None,
            'errors': errors,
            'active': 'summary',
            'results_summary': summary,
            'job_input': job.read_input_file('in'),
            'job_options': job.read_input_file('options'),
            }
        return render(request, 'search/results_all.html', context)
    else:
        context = {
            'status_msg': status_msg,
            'job': job,
            'page_title': page_title,
            'recent_jobs': set_and_get_session_jobs(request, job),
            'structure_models': [],
            'generated_msas': [],
            'sequences': [],
            'reload': refresh,
            'log': '' if removed else job.calculation_log,
            'errors': '' if removed else errors,
            'active': 'not_finished',
            'job_input': '' if removed else job.read_input_file('in'),
            'job_options': '' if removed else job.read_input_file('options'),
            }
        return render(request, 'jobs/not_finished_or_removed.html', context)


class ApiResultsJson(ApiResultsView):
    "API view showing results in JSON format"
    def format_output(self, job, sequence_no=None):
        result = self.start_output_for_successful_result(job)
        result['number_of_input_queries'] = job.number_of_input_queries
        result['number_of_successful_queries'] = \
            job.number_of_successful_queries or 0
        result['results'] = []
        if job.status == job.FINISHED:
            results_files = job.read_results_lst()
            for rf in results_files:
                results_json_file = job.results_file_path(rf['results_json'])
                sequence_results, err = utils.read_json_file(results_json_file)
                result['results'].append(sequence_results)
        result['web_url'] = reverse(results, kwargs={'job_id': job.name})
        return JsonResponse(result)


class ApiResultsDownloadFile(ApiResultsView):
    "Base API view for retrieving results files"
    def format_output(self, job, sequence_no=None):
        rf = job.results_file_path(self.fname(job, sequence_no))
        if os.path.isfile(rf):
            return FileResponse(open(rf, 'rb'))
        else:
            print('File %s not found!' % rf)
            return HttpResponse('File not found!\n')


class ApiResultsZip(ApiResultsDownloadFile):
    def fname(self, job, sequence_no=None):
        return job.get_output_name()+'.tar.gz'


class ApiJobOptions(ApiResultsDownloadFile):
    def fname(self, job, sequence_no=None):
        return job.results_file_path(job.name+'.options')


class ApiJobInput(ApiResultsDownloadFile):
    def fname(self, job, sequence_no=None):
        return job.results_file_path(job.name+'.in')


class ApiJobError(ApiResultsDownloadFile):
    def fname(self, job, sequence_no=None):
        return job.results_file_path(job.name+'.err')


class ApiDetailedDownloadInput(ApiResultsDownloadFile):
    def fname(self, job, sequence_no):
        results_file = job.results_file(sequence_no, 'input')
        return results_file


class ApiDetailedDownloadProfile(ApiResultsDownloadFile):
    def fname(self, job, sequence_no):
        results_file = job.results_file(sequence_no, 'profile')
        return results_file


class ApiDetailedDownloadMSA(ApiResultsDownloadFile):
    def fname(self, job, sequence_no):
        results_file = job.results_file(sequence_no, 'msa')
        return results_file


class ApiDetailedDownloadJSON(ApiResultsDownloadFile):
    def fname(self, job, sequence_no):
        results_file = job.results_file(sequence_no, 'results_json')
        return results_file


def detailed(request, job_id, result_no):
    job = utils.get_object_or_404_for_removed_also(models.Job, name=job_id)
    print(job)
    results_files = job.read_results_lst()
    results_file = job.results_file_path(
        results_files[result_no]['results_json']
        )
    results, json_error = utils.read_json_file(results_file)
    if results is None:
        return render(request, 'search/error.html', {'json_error': json_error})
    input_file = job.results_file_path(results_files[result_no]['input'])
    input_name, input_format, input_description = \
        models.read_input_name_and_type(input_file)
    page_title = '%s results - %s - %s' % (
        job.method().upper(), job.nice_name(), input_name
        )
    context = {
        'job': job,
        'page_title': page_title,
        'recent_jobs': set_and_get_session_jobs(request, job),
        'structure_models': job.get_structure_models(result_no),
        'generated_msas': job.get_generated_msas().get(result_no, []),
        'sequence_no': result_no,
        'sequences': job.sequence_headers(),
        'results': results,
        'input_name': input_name,
        'input_description': input_description,
        'input_format': '' if input_format is None else f' ({input_format})',
        'has_msa': results_files[result_no]['msa'],
        'active': 'detailed',
        }
    return render(request, 'search/results.html', context)


def detailed_summary(request, job_id, sequence_no):
    job = utils.get_object_or_404_for_removed_also(models.Job, name=job_id)
    results_files = job.read_results_lst()
    result_summary = models.SearchResultsSummary(job, results_files[sequence_no])
    if result_summary.results_json is None:
        return render(
            request, 'search/error.html',
            {'json_error': result_summary.json_error}
            )
    sequences = job.sequence_headers()
    page_title = '%s results - %s - %s' % (
        job.method().upper(), job.nice_name(), sequences[sequence_no]
        )
    context = {
        'job': job,
        'page_title': page_title,
        'recent_jobs': set_and_get_session_jobs(request, job),
        'structure_models': job.get_structure_models(sequence_no),
        'generated_msas': job.get_generated_msas().get(sequence_no, []),
        'sequence_no': sequence_no,
        'sequences': sequences,
        'active': 'query_summary',
        'has_msa': results_files[sequence_no]['msa'],
        'r': result_summary,
        }
    return render(request, 'search/query_summary.html', context)


def show_input(request, job_id, sequence_no=None):
    job = utils.get_object_or_404_for_removed_also(models.Job, name=job_id)
    print(job)
    page_title = '%s input - %s' % (job.method().upper(), job.nice_name())
    if sequence_no is None:
        input_file = job.get_input_file('in')
        input_name = None
    else:
        results_files = job.read_results_lst()
        input_file = job.results_file_path(results_files[sequence_no]['input'])
        input_name, input_format, input_description = \
            models.read_input_name_and_type(input_file)
    with open(input_file) as f:
        input_data = f.read()
    if input_name:
        page_title += ' - %s' % input_name
    context = {'input_str': input_data, 'page_title': page_title}
    return render(
            request, 'search/detailed_input.html', context
            )

