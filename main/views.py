from urllib import request
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect
from django.conf import settings
from django.views import View
from django.contrib import messages

from .mongo.samples_api import API
from .models import UserProfile, DataSet

api = API(settings.MONGO_CONNECTION, settings.MONGO_FIELD_MAPPING)

def get_context(request):
        user_profile = UserProfile.objects.get_or_create(user=request.user)[0]
        return user_profile

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
def sample_list(request, dataset_key:int=None):
    user_profile = get_context(request)
    if dataset_key:
        dataset = DataSet.objects.get(pk=dataset_key)
        species = dataset.species
    else:
        dataset = None
        species = None
    species_name = get_species_name(species)
    samples = list(api.get_samples(species_name=species_name))
    print(f"***Dataset: {dataset}")
    for sample in samples:
        sample['id'] = str(sample['_id'])
        if dataset:
            sample['in_dataset'] = sample['id'] in dataset.mongo_ids
        else:
            sample['in_dataset'] = False
    return render(request, 'main/sample_list.html',{
        'user_profile': user_profile,
        'species_name': species_name,
        'samples': samples,
        'dataset': dataset
        })


class DataSetView(View):
    edit:bool=False

    @method_decorator(login_required)
    def get(self, request, dataset_key:int=None):
        user_profile = get_context(request)
        if dataset_key:
            dataset = DataSet.objects.get(pk=dataset_key)
            if self.edit and dataset.owner != request.user:
                messages.add_message(request, messages.ERROR, 'You tried to edit a dataset that you do not own.')
                return redirect(dataset_list)
            species = dataset.species
        else:
            dataset = None
            species = None
        species_name = get_species_name(species)
        samples = list(api.get_samples(species_name=species_name))
        for sample in samples:
            sample['id'] = str(sample['_id'])
            if dataset:
                sample['in_dataset'] = sample['id'] in dataset.mongo_ids
            else:
                sample['in_dataset'] = False
        return render(request, 'main/sample_list.html',{
            'user_profile': user_profile,
            'species_name': species_name,
            'samples': samples,
            'dataset': dataset,
            'edit': self.edit
            })


@login_required
def dataset_list(request):
    user_profile = get_context(request)
    datasets = DataSet.objects.all()
    return render(request, 'main/dataset_list.html',{
        'user_profile': user_profile,
        'datasets': datasets
        })