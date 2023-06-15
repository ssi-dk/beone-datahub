import json
from re import template
from pathlib import Path

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse, StreamingHttpResponse
from django.conf import settings
from django.contrib import messages
from django.urls import reverse
from django.db import IntegrityError
from django.contrib.auth.models import User

from bio_api.mongo.samples import API
from main.models import DataSet, RTJob, Partition,  Cluster, parse_rt_output
from comparisons.forms import NewDatasetForm, DeleteDatasetForm, DashboardLauncherForm

api = API(settings.MONGO_CONNECTION)


def get_species_name(species: str=None):
    for s in settings.ALL_SPECIES:
        if s[0] == species:
            return s[1]
    # If a full species name was not found, return shortname
    return species


def redirect_root(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/sequence_sets/')
    else:
        return HttpResponseRedirect('/login/')
    

@login_required
def sample_list(request):
    fields_to_get = { entry[0] for entry in settings.SAMPLE_VIEW_COLUMNS }
    samples = api.get_samples(fields=fields_to_get)
    return render(request, 'main/sample_list.html',{
        'samples': samples,
        })


@login_required
def dataset_list(request):
    datasets = DataSet.objects.all()

    if request.method == 'POST':
            form = NewDatasetForm(request.POST)
            if form.is_valid():
                dataset = DataSet(
                    owner=request.user,
                    species=form.cleaned_data['species'],
                    name=form.cleaned_data['name'],
                    description=form.cleaned_data['description'])
                try:
                    dataset.save()
                    messages.add_message(request, messages.ERROR,
                    'A new empty dataset was created. Use the Edit function to add samples to it.')
                except IntegrityError:
                     messages.add_message(request, messages.ERROR, 
                     'Dataset was not created. Probably there was already a dataset with that name.')
                return HttpResponseRedirect(reverse(dataset_list))
            
    else:
        form = NewDatasetForm()

    return render(request, 'main/dataset_list.html',{
        'form': form,
        'datasets': datasets
        })


@login_required
def view_dataset(request, dataset_key:int):
    dataset = DataSet.objects.get(pk=dataset_key)
    species_name = get_species_name(dataset.species)
    fields_to_get = { entry[0] for entry in settings.SAMPLE_VIEW_COLUMNS }
    samples, unmatched = api.get_samples_from_keys(dataset.mongo_keys, fields=fields_to_get)
    if len(unmatched) != 0:
        messages.add_message(request, messages.WARNING, f'Some keys in the dataset are unmatched: {unmatched}')

    return render(request, 'main/sample_list.html',{
        'species_name': species_name,
        'samples': samples,
        'dataset': dataset,
        'edit': False
        })


@login_required
def edit_dataset(request, dataset_key:int):
    dataset = DataSet.objects.get(pk=dataset_key)
    species_name = get_species_name(dataset.species)
    if not dataset.owner in [request.user, None]:
        messages.add_message(request, messages.ERROR, f'You tried to edit the dataset {dataset.name}, which you do not own.')
        return redirect(dataset_list)
    
    if request.method == 'POST':
        form = DeleteDatasetForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['confirm_name'] == dataset.name:
                dataset.delete()
                messages.add_message(request, messages.INFO, f'Dataset {dataset.name} was deleted.')
                return HttpResponseRedirect('/datasets/')

    form = DeleteDatasetForm()
    fields_to_get = { entry[0] for entry in settings.SAMPLE_VIEW_COLUMNS }
    if dataset.species == 'mixed':
         samples = list(api.get_samples(fields=fields_to_get))
    else:
        samples = list(api.get_samples(species_name=species_name, fields=fields_to_get))
    for sample in samples:
        for key_pair in dataset.mongo_keys:
            if key_pair['org'] == sample['org'] and key_pair['name'] == sample['name']:
                sample['in_dataset'] = True

    return render(request, 'main/sample_list.html',{
        'species_name': species_name,
        'delete_form': form,
        'samples': samples,
        'dataset': dataset,
        'edit': True
        })


def add_remove_sample(request):
    """
    update_mongids.js sends this in POST request:
        "username": document.getElementById('username').innerText,
        "datasetName": document.getElementById("dataset_name").innerText,
        "datasetKey": document.getElementById("dataset_key").innerText,
        "mongoId": {"org": <org>, "name": <name>}
        "action": 'add' | 'remove'
    """
    data_from_post = json.load(request)
    request_user = User.objects.get(username=data_from_post['username'])
    dataset = DataSet.objects.get(pk=data_from_post['datasetKey'])
    if not dataset.owner in [request_user, None]:
        data_to_send = {
            'status':'ERROR',
            'message': 'Dataset is owned by another user.'
        }
    else:
        mongo_id = data_from_post['mongoId']
        if data_from_post['action'] == 'add':
            try:
                dataset.mongo_keys.append(mongo_id)
                dataset.save()
                data_to_send = {
                    'status': 'OK',
                    'message': f'Sample {mongo_id} was added to dataset.'
                }
            except Exception as e:
                data_to_send = {
                'status':'ERROR',
                'message': str(e)
            }
        if data_from_post['action'] == 'remove':
            try:
                dataset.mongo_keys.remove(data_from_post['mongoId'])
                dataset.save()
                data_to_send = {
                    'status': 'OK',
                    'message': f'Sample {mongo_id} was removed from dataset.'
                }
            except Exception as e:
                data_to_send = {
                'status':'ERROR',
                'message': str(e)
            }
    return JsonResponse(data_to_send)

        
@login_required
def rt_jobs(request, dataset_key:str=None):
    if dataset_key is not None:
        dataset = DataSet.objects.get(pk=dataset_key)
        if request.method == 'POST':
            rt_job = RTJob(owner=request.user, dataset=dataset)
            rt_job.save()
        rt_jobs = RTJob.objects.filter(dataset=dataset_key) 
    else:
        rt_jobs = RTJob.objects.all()
        dataset = None
    return render(request, 'main/rt_jobs.html',{
        'rt_jobs': rt_jobs,
        'dataset': dataset
        })


@login_required
def delete_rt_job(request, rt_job_key:str, dataset_page:bool=False):
    rt_job = RTJob.objects.get(pk=rt_job_key)
    dataset = rt_job.dataset
    if rt_job.status != 'NEW':
        messages.add_message(request, messages.ERROR, f'You can only delete a job that has status NEW.')
    else:
        rt_job.delete()
    if dataset_page:
        return HttpResponseRedirect(f'/comparisons/for_dataset/{dataset.pk}')
    return HttpResponseRedirect('/comparisons/')


@login_required
def run_rt_job(request, rt_job_key:str):
    rt_job = RTJob.objects.get(pk=rt_job_key)
    dataset = rt_job.dataset
    if len(dataset.mongo_keys) == 0:
        messages.add_message(request, messages.ERROR, f'You tried to run ReporTree on an empty dataset.')
    elif rt_job.status not in ['NEW', 'READY']:
        messages.add_message(request, messages.ERROR, f'You tried to run a ReporTree job that has alreay been run.')
    else:
        # Make sure we get the necessary fields from MongoDB.
        pseudo_fields = set()
        pseudo_fields.add( 'allele_profile')
        """TODO Note for a future improvement: instead of hardcoding the allele profile fields this way,
        the RT job could have a field for which mongo field contains the allele profile. This would add more flexibility
        so that different RT jobs could use different allele schemas stores in different Mongo fields.
        However, this would imply that the API should be enhanced so we could specify fields directly as mongo fields instead of
        'pseudo fields' (that need to go through MONGO_FIELD_MAPPING to get the real mongo fields).
        """
        # for metadata_field in rt_job.metadata_fields:
        #     pseudo_fields.add(metadata_field)
        mongo_cursor, unmatched = api.get_samples_from_keys(dataset.mongo_keys, fields=pseudo_fields)
        if len(unmatched) != 0:
            messages.add_message(request, messages.ERROR, f'Some keys in the dataset are unmatched: {unmatched}. Please fix before running job.')
        else:
            rt_job.prepare(mongo_cursor)
            rt_job.run()
            # if rt_job.update_status() == 'SUCCESS':
            #     parse_rt_output(rt_job)

    return HttpResponseRedirect(f'/comparisons/for_dataset/{dataset.pk}')


@login_required
def view_rt_job(request, rt_job_key:str):
    rt_job = RTJob.objects.get(pk=rt_job_key)
    # if rt_job.status == 'SUCCESS':
    #     parse_rt_output(rt_job)
    species_name = get_species_name(rt_job.dataset.species)
    form = DashboardLauncherForm()
    return render(request, 'main/rt_job.html',{
        'rt_job': rt_job,
        'species_name': species_name,
        'form': form.as_p
        })

@login_required
def view_rt_output(request, rt_job_key:str, item: str='log'):
    rt_job = RTJob.objects.get(pk=rt_job_key)
    if item == 'log':
        content = rt_job.log
    if item == 'newick':
        content = rt_job.newick

    content_lines = content.split('\n')

    return render(request, 'main/raw_file.html',{
        'rt_job': rt_job,
        'item': item,
        'content_lines': content_lines
        })

@login_required
def download_rt_file(request, rt_job_key:str, item: str='log'):
    rt_job: RTJob = RTJob.objects.get(pk=rt_job_key)
    if item == 'log':
        file = rt_job.get_log_path()
        content_type = 'text/plain'
    if item == 'newick':
        file = rt_job.get_newick_path()
        content_type = 'text/plain'
    if item == 'partitions_summary':
        file = rt_job.get_partitions_summary_path()
        content_type = 'tab-separated-values'
    if item == 'metadata_w_partitions':
        file = rt_job.get_metadata_w_partitions_path()
        content_type = 'tab-separated-values'
    if item == 'clusters':
        file = rt_job.get_cluster_path()
        content_type = 'tab-separated-values'
    if item == 'partitions':
        file = rt_job.get_partitions_path()
        content_type = 'tab-separated-values'
    if item == 'summary':
        file = rt_job.get_partitions_summary_path()
        content_type = 'tab-separated-values'
    if item == 'distances':
        file = rt_job.get_distance_matrix_path()
        content_type = 'tab-separated-values'
    if item == 'metapart':
        file = rt_job.get_metadata_w_partitions_path()
        content_type = 'tab-separated-values'

    file_name = str(rt_job.pk) + '_' + file.name
    stream = open(file, 'r')

    return StreamingHttpResponse(
        streaming_content=stream,
        content_type=content_type,
        headers={'Content-Disposition': f'attachment; filename="{file_name}"'},
    )

@login_required
def get_rt_data(request, rt_job_key: str):
    rt_job = RTJob.objects.get(pk=rt_job_key)
    return JsonResponse({'newick': rt_job.newick, 'sample_ids': rt_job.dataset.mongo_keys})

@login_required
def get_partitions_for_job(request, rt_job_key: str):
    rt_partitions = Partition.objects.filter(rt_job=rt_job_key)
    partition_dict = dict()
    for p in rt_partitions:
        cluster_list = list()
        for c in p.cluster_set.all():
            cluster_dict = {'name': c.name}
            cluster_dict['samples'] = list(c.samples)
            cluster_list.append(cluster_dict)
        partition_dict[p.name] = cluster_list

    response = {'rt_job': rt_job_key, 'partitions': partition_dict}
    return JsonResponse(response)