from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.conf import settings

from .mongo.samples_api import API
from .forms import SpeciesForm
from .models import UserProfile, DataSet

api = API(settings.MONGO_CONNECTION, settings.MONGO_FIELD_MAPPING)

def get_context(request):
        user_profile = UserProfile.objects.get_or_create(user=request.user)[0]
        return user_profile


@login_required
def sample_list(request):
    user_profile = get_context(request)
    species_name = 'all' # Todo: take from request arguments
    samples = list(api.get_samples_of_species(species_name))
    return render(request, 'main/sample_list.html',{
        'user_profile': user_profile,
        'species_name': species_name,
        'samples': samples
        })


@login_required
def data_sets(request):
    user_profile = get_context(request)
    data_sets = DataSet.objects.all()
    return render(request, 'main/data_sets.html',{
        'user_profile': user_profile,
        'data_sets': data_sets
        })