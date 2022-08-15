from urllib import request
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.conf import settings

from .mongo.samples_api import API
from .models import UserProfile, DataSet

api = API(settings.MONGO_CONNECTION, settings.MONGO_FIELD_MAPPING)

def get_context(request):
        user_profile = UserProfile.objects.get_or_create(user=request.user)[0]
        return user_profile

def get_species_name(species: str=None):
    if species is None:
        return('all')
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
def sample_list(request, species:str=None):
    user_profile = get_context(request)
    species_name = get_species_name(species)
    samples = list(api.get_samples_of_species(species_name))
    if 'dataset' in request.GET:
        dataset_pk = request.GET['dataset']
        data_set = DataSet.objects.get(pk=dataset_pk)
    else:
        data_set = None
    for sample in samples:
        sample['id'] = str(sample['_id'])
        if data_set:
            sample['in_dataset'] = sample['id'] in data_set.mongo_ids
        else:
            sample['in_dataset'] = False
    return render(request, 'main/sample_list.html',{
        'user_profile': user_profile,
        'species_name': species_name,
        'samples': samples,
        'data_set': data_set
        })


@login_required
def data_sets(request):
    user_profile = get_context(request)
    data_sets = DataSet.objects.all()
    return render(request, 'main/data_sets.html',{
        'user_profile': user_profile,
        'data_sets': data_sets
        })