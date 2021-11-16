import os
import copy

from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse, JsonResponse, FileResponse, \
        QueryDict
from django.conf import settings
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse

from . import forms
from . import default
from . import models
from apps.core import utils

def input(request):
    "View to input query sequences or MSA"
    InputForm = forms.SequencesInputForm

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
        'form': form,
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
            'comer_db', settings.COMER_DATABASES[0][0]
            )
        input_data_and_settings.setdefault(
            'cother_db', settings.COTHER_DATABASES[0][0]
            )
        input_data_and_settings.setdefault(
            'hhsuite_db', settings.HHSUITE_DATABASES[0][0]
            )
        input_data_and_settings.setdefault(
            'sequence_db', settings.SEQUENCE_DATABASES[0][0]
            )
        form = forms.SequencesInputFormWithAllSettings(
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


def results(request, job_id):
    job = get_object_or_404(models.Job, name=job_id)
    print(job)
    finished, removed, status_msg, errors, refresh = job.status_info()
    if finished and not removed:
        if job.number_of_input_sequences == 1:
            print('Single-sequence job, redirecting.')
            return redirect('detailed', job_id=job_id, sequence_no=0)

        sequences = job.sequence_headers()
        context = {
            'job': job,
            'sequences': sequences,
            'sequence_no': None,
            'errors': errors,
            'active': 'summary',
            }
        return render(request, 'search/results_all.html', context)
    else:
        return render(
                request, 'jobs/not_finished_or_removed.html',
                {'status_msg': status_msg, 'reload': refresh,
                    'log': job.calculation_log, 'errors': errors
                    }
                )


class ApiResultsJson(ApiResultsView):
    "API view showing results in JSON format"
    def format_output(self, job, sequence_no=None):
        result = self.start_output_for_successful_result(job)
        result['number_of_input_sequences'] = job.number_of_input_sequences
        result['number_of_successful_sequences'] = \
            job.number_of_successful_sequences or 0
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


def detailed(request, job_id, sequence_no):
    job = get_object_or_404(models.Job, name=job_id)
    print(job)
    results_files = job.read_results_lst()
    results_file = job.results_file_path(
        results_files[sequence_no]['results_json']
        )
    results, json_error = utils.read_json_file(results_file)
    if results is None:
        return render(request, 'search/error.html', {'json_error': results})
    input_file = job.results_file_path(results_files[sequence_no]['input'])
    input_name, input_format, input_description = \
        models.read_input_name_and_type(input_file)
    context = {
        'job': job,
        'sequence_no': sequence_no,
        'sequences': job.sequence_headers(),
        'results': results, 'input_name': input_name,
        'input_description': input_description,
        'input_format': '' if input_format is None else f' ({input_format})',
        'has_msa': results_files[sequence_no]['msa'],
        'active': 'detailed',
        }
    return render(request, 'search/results.html', context)


def show_input(request, job_id, sequence_no=None):
    job = get_object_or_404(models.Job, name=job_id)
    print(job)
    if sequence_no is None:
        input_file = job.get_input_file('in')
    else:
        results_files = job.read_results_lst()
        input_file = job.results_file_path(results_files[sequence_no]['input'])
    with open(input_file) as f:
        input_data = f.read()
    return render(
            request, 'search/detailed_input.html', {'input_str': input_data}
            )

