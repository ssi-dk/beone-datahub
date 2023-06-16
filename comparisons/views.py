import json

from bio_api.mongo.samples import API

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse, StreamingHttpResponse
from django.conf import settings
from django.contrib import messages
from django.urls import reverse
from django.db import IntegrityError
from django.contrib.auth.models import User

from comparisons.models import Species, DistanceMatrix, Tree, SequenceSet, Comparison
from comparisons.forms import NewComparisonForm, DeleteDatasetForm, DashboardLauncherForm

# TODO Remove
from main.models import DataSet, RTJob, Partition

api = API(settings.MONGO_CONNECTION)


def redirect_root(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/comparisons/')
    else:
        return HttpResponseRedirect('/login/')
    

@login_required
def sample_list(request):
    fields_to_get = { entry[0] for entry in settings.SAMPLE_VIEW_COLUMNS }
    samples = api.get_samples(fields=fields_to_get)
    return render(request, 'comparisons/sample_list.html',{
        'samples': samples,
        })


@login_required
def comparison_list(request):
    comparisons = Comparison.objects.all()

    if request.method == 'POST':
            form = NewComparisonForm(request.POST)
            if form.is_valid():
                comparison = Comparison(
                    created_by=request.user,
                    species=form.cleaned_data['species'],
                    sequences=form.cleaned_data['sequences'],
                )
                try:
                    comparison.save()
                    messages.add_message(request, messages.SUCCESS,
                    'New comparison created')
                except Exception as e:
                     messages.add_message(request, messages.ERROR, e)
                return HttpResponseRedirect(reverse(comparison_list))
            
    else:
        form = NewComparisonForm()

    return render(request, 'comparisons/comparisons.html',{
        'form': form,
        'comparisons': comparisons
        })
