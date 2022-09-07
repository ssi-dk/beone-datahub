import pathlib
import json

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.conf import settings
from django.contrib import messages
from django.urls import reverse
from django.db import IntegrityError
from django.contrib.auth.models import User

from main.mongo.samples_api import API
from main.models import DataSet, RTJob
from main.forms import NewDatasetForm, DeleteDatasetForm

api = API(settings.MONGO_CONNECTION, settings.MONGO_FIELD_MAPPING)


def get_species_name(species: str=None):
    if species is None:
        return None
    for s in settings.ALL_SPECIES:
        if s[0] == species:
            return s[1]
    # If a full species name was not found, return shortname
    return species

def redirect_root(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/sample_list/')
    else:
        return HttpResponseRedirect('/login/')
    

@login_required
def sample_list(request):
    samples = api.get_samples()
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
    samples, unmatched = api.get_samples_from_keys(dataset.mongo_keys)
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
    if dataset.owner != request.user:
        messages.add_message(request, messages.ERROR, f'You tried to edit the dataset {dataset.name}, which you do not own.')
        return redirect(dataset_list)
    
    if request.method == 'POST':
        print("POST")
        form = DeleteDatasetForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['confirm_name'] == dataset.name:
                dataset.delete()
                messages.add_message(request, messages.INFO, f'Dataset {dataset.name} was deleted.')
                return HttpResponseRedirect('/datasets/')

    form = DeleteDatasetForm()
    samples = list(api.get_samples(species_name=species_name))
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
    if not request_user == dataset.owner:
        data_to_send = {
            'status':'ERROR',
            'message': 'Request user is not dataset owner.'
        }
    else:
        mongo_id = data_from_post['mongoId']
        print(mongo_id)
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
        return HttpResponseRedirect(f'/rt_jobs/for_dataset/{dataset.pk}')
    return HttpResponseRedirect('/rt_jobs/')

def add_sample_data_in_files(sample, tsv_file):
    allele_profile = sample['allele_profile']
    allele_list = list()
    for allele in allele_profile:
        allele_value = allele['allele_crc32']  # Maybe choose key name with a setting
        if allele_value is None:
            allele_list.append('-')
        else:
            allele_list.append(str(allele_value))
    tsv_file.write('\t'.join(allele_list))
    tsv_file.write('\n')

@login_required
def run_rt_job(request, rt_job_key:str):
    rt_job = RTJob.objects.get(pk=rt_job_key)
    dataset = rt_job.dataset
    if len(dataset.mongo_keys) == 0:
        messages.add_message(request, messages.ERROR, f'You tried to run ReporTree on an empty dataset.')
    elif rt_job.status not in ['NEW', 'READY']:
        messages.add_message(request, messages.ERROR, f'You tried to run a ReporTree job that has alreay been run.')
    else:
        samples, unmatched = api.get_samples_from_keys(dataset.mongo_keys, fields={'allele_profile'})
        if len(unmatched) != 0:
            messages.add_message(request, messages.ERROR, f'Some keys in the dataset are unmatched: {unmatched}. Please fix before running job.')
        else:
            # Create a folder for the run
            root_folder = pathlib.Path('/rt_runs')
            if not root_folder.exists():
                root_folder.mkdir()
            job_folder = pathlib.Path(root_folder, str(rt_job_key))
            if job_folder.exists():
                print(f"Job folder {job_folder} already exists! Reusing it.")
            else:
                job_folder.mkdir()
                print(f"Created job folder {job_folder}.")
            
            tsv_file = open(pathlib.Path(job_folder, 'allele_profiles.tsv'), 'w')
            metadata_file = open(pathlib.Path(job_folder, 'metadata.tsv'), 'w')
            
            # Get allele profile for first sample so we can define TSV header
            header_list = list()
            first_sample = next(samples)
            for allele in first_sample['allele_profile']:
                locus = allele['locus']
                if locus.endswith('.fasta'):
                    locus = locus[:-6]
                header_list.append(locus)
            tsv_file.write('\t'.join(header_list))
            tsv_file.write('\n')

            # Write data for first sample to files
            add_sample_data_in_files(first_sample, tsv_file)

            # Write data for subsequent samples to files
            for sample in samples:
                add_sample_data_in_files(sample, tsv_file)
            
            tsv_file.close()
            metadata_file.close()
        
            # Set new status on job
            rt_job.initialize()
    return HttpResponseRedirect(f'/rt_jobs/for_dataset/{dataset.pk}')