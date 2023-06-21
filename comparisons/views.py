import json

import requests

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse, StreamingHttpResponse
from django.conf import settings
from django.contrib import messages
from django.urls import reverse
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.utils import timezone

from bio_api.mongo.samples import API
from comparisons.models import Species, DistanceMatrix, Tree, SequenceSet, Comparison
from comparisons.forms import NewComparisonForm, DeleteDatasetForm, DashboardLauncherForm

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

    return render(request, 'comparisons/comparison_list.html',{
        'form': form,
        'comparisons': comparisons
        })


@login_required
def make_tree(request, comparison_id, treetype):
    comparison = Comparison.objects.get(pk=comparison_id)
    if treetype not in ['single', 'complete']:
        messages.add_message(request, messages.ERROR, f'Unknown treetype: {request.treetype}')
    else:
        # Do different things depending on distance matrix status
        # if comparison.status == 'DM_OK':
        if comparison.status == 'laskjdhlasudhyf':  #TODO: remove
            print(f"Reusing previous distance matrix for comparison {comparison.id}")
        else:
            # get distance matrix
            print(f"Requesting distance matrix for comparison {comparison.pk}")
            comparison.status = 'DM_REQ'
            comparison.save()
            start_time = timezone.now()
            raw_response = requests.post(f'http://bio_api:{str(settings.BIO_API_PORT)}/distance_matrix/from_ids',
                json={'sequence_ids': comparison.sequences})
            json_response = (raw_response.json())
            if 'distance_matrix' in json_response:
                comparison.distances = json_response['distance_matrix']
                comparison.status = "DM_OK"
                end_time = timezone.now()
                elapsed_time = (end_time - start_time).seconds
                msg = f"Distance matrix generation for comparison with id {comparison.id } took {elapsed_time} seconds"
                print(msg)
                messages.add_message(request, messages.INFO, msg)
                comparison.save()  # Make sure we have the distance matrix in case we don't get the tree
            else:
                comparison.status = "DM_ERR"
                comparison.save()
                msg = f"Error getting distance matrix for comparison {comparison.id}: no distance matrix in response"
                print(msg)
                messages.add_message(request, messages.INFO, msg)

        raw_response = requests.post(f'http://bio_api:{str(settings.BIO_API_PORT)}/tree/hc/',
                json={
                    'distances': comparison.distances,
                    'method': treetype
                    })
        comparison.save()
    return HttpResponseRedirect(reverse(comparison_list))