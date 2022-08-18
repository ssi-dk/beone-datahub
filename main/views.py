from urllib import request
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect
from django.conf import settings
from django.views import View
from django.contrib import messages
from django.urls import reverse

from .mongo.samples_api import API
from .models import UserProfile, DataSet
from .forms import NewDatasetForm

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
def sample_list(request):
    user_profile = get_context(request)
    samples = list(api.get_samples())
    for sample in samples:
        sample['id'] = str(sample['_id'])
    return render(request, 'main/sample_list.html',{
        'user_profile': user_profile,
        'samples': samples,
        })


@login_required
def dataset_list(request):
    user_profile = get_context(request)
    datasets = DataSet.objects.all()

    if request.method == 'POST':
            form = NewDatasetForm(request.POST)
            if form.is_valid():
                dataset = DataSet(
                    owner=request.user,
                    species=form.cleaned_data['species'],
                    name=form.cleaned_data['name'],
                    description=form.cleaned_data['description'])
                dataset.save()
                return HttpResponseRedirect(reverse(dataset_list))
    else:
        form = NewDatasetForm()

    return render(request, 'main/dataset_list.html',{
        'user_profile': user_profile,
        'form': form,
        'datasets': datasets
        })


class DataSetView(View):
    edit:bool=False

    @method_decorator(login_required)
    def get(self, request, dataset_key:int):
        user_profile = get_context(request)
        dataset = DataSet.objects.get(pk=dataset_key)
        species_name = get_species_name(dataset.species)
        if self.edit:
            if dataset.owner != request.user:
                messages.add_message(request, messages.ERROR, 'You tried to edit a dataset that you do not own.')
                return redirect(dataset_list)
            samples = list(api.get_samples(species_name=species_name))
            for sample in samples:
                sample['id'] = str(sample['_id'])
                sample['in_dataset'] = sample['id'] in dataset.mongo_ids
        else:
            if len(dataset.mongo_ids) > 0:
                samples = list(api.get_samples(mongo_ids=dataset.mongo_ids))
                for sample in samples:
                    sample['id'] = str(sample['_id'])
            else:
                # Empty dataset
                samples = list()
        return render(request, 'main/sample_list.html',{
            'user_profile': user_profile,
            'species_name': species_name,
            'samples': samples,
            'dataset': dataset,
            'edit': self.edit
            })
