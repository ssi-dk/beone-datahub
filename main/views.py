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
        species_name = user_profile.get_current_species_display()
        return user_profile, species_name


def sample_list(request):
    if request.user.is_authenticated:
        user_profile, species_name = get_context(request)
        samples = list(api.get_samples_of_species(species_name))
        return render(request, 'main/sample_list.html',{
            'user_profile': user_profile,
            'species_name': species_name,
            'samples': samples
            })
    else:
        return render(request, 'main/base.html')


@login_required
def data_sets(request):
    user_profile, species_name = get_context(request)
    data_sets = DataSet.objects.all()
    return render(request, 'main/data_sets.html',{
        'user_profile': user_profile,
        'species_name': species_name,
        'data_sets': data_sets
        })

@login_required
def select_species(request):
    user_profile, species_name = get_context(request)
    if request.method == 'POST':
        form = SpeciesForm(request.POST)
        if form.is_valid():
            user_profile.current_species = form.cleaned_data['species']
            user_profile.save()
            return HttpResponseRedirect('/')
        
    else:
        form = SpeciesForm(initial={'species': user_profile.current_species},
        )
        return render(request, 'main/select_species.html', {
            'user_profile': user_profile,
            'species_name': species_name,
            'form': form
            })