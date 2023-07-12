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

from bio_api.mongo.samples import MongoAPI
from comparisons.models import Species, Tree, SequenceSet, Comparison
from comparisons.forms import NewComparisonForm

TREE_TYPE_IDS = [ t[0] for t in Tree.TREE_TYPES ]

api = MongoAPI(settings.MONGO_CONNECTION)

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
                    tool=form.cleaned_data['tool'],
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
def make_tree(request, comparison_id, tree_type):
    comparison = Comparison.objects.get(pk=comparison_id)
    if tree_type not in TREE_TYPE_IDS:
        messages.add_message(request, messages.ERROR, f'Unknown tree type: {tree_type}')
    else:
        # Do different things depending on distance matrix status
        if comparison.dm_status in ('NODATA', 'ERROR', 'OBSOLETE') or comparison.always_calculate_dm:
            # Get distance matrix
            print(f"Requesting distance matrix for comparison {comparison.pk}")
            comparison.dm_status = 'PENDING'
            comparison.save()
            start_time = timezone.now()
            raw_response = requests.post(
                f'http://bio_api:{str(settings.BIO_API_PORT)}/distance_matrix/from_ids',
                json={'sequence_ids': comparison.sequences},
                timeout=5)
            json_response = (raw_response.json())
            if not 'error' in json_response:
                dist_mx_records = json_response['distance_matrix']
                print("Distance matrix received:")
                print(dist_mx_records)
                comparison.distances = dist_mx_records
                comparison.dm_status = "VALID"
                end_time = timezone.now()
                elapsed_time = (end_time - start_time).seconds
                msg = f"Distance matrix generation for comparison with id {comparison.id } took {elapsed_time} seconds"
                print(msg)
                messages.add_message(request, messages.INFO, msg)
                comparison.save()  # Make sure we have the distance matrix in case we don't get the tree
            else:
                msg = f"Error getting distance matrix for comparison {comparison.id}"
                messages.add_message(request, messages.ERROR, msg)
                print(msg)
                print(json_response)
                messages.add_message(request, messages.ERROR, json_response['error'])
                if 'unmatched' in json_response:
                    print("Unmatched:")
                    print(json_response['unmatched'])
                comparison.dm_status = "ERROR"
                comparison.save()
                return HttpResponseRedirect(reverse(comparison_list))
        elif comparison.dm_status == 'PENDING':
            msg = (f"There is already a pending distance matrix request for comparison {comparison.id}")
            print(msg)
            messages.add_message(request, messages.ERROR, msg)
            return HttpResponseRedirect(reverse(comparison_list))
        else:
            assert comparison.dm_status == 'VALID'  # We should only end up here in case dm_status is VALID
            print(f"Reusing previous distance matrix for comparison {comparison.id}")

        # Get tree
        print("This is what distances loook like in db:")
        print(comparison.distances)
        index = comparison.distances['index']
        columns = comparison.distances['columns']
        data = comparison.distances['data']
        assert index == columns
        matrix_size = len(columns)
        assert matrix_size == len(data)
        dm = dict()
        for i in range(matrix_size):
            dm[columns[i]] = data[i]
        print("This is the distance matrix I'll send to Bio API:")
        print(dm)
        print(f"Requesting tree for comparison {comparison.pk}, tree type {tree_type}")
        raw_response = requests.post(f'http://bio_api:{str(settings.BIO_API_PORT)}/tree/hc/',
                json={
                    'distances': dm,
                    'method': tree_type
                    })
        json_response = (raw_response.json())
        print("JSON response:")
        print(json_response)
        if 'tree' in json_response:
            msg = f"Received tree with method {tree_type} for comparison with id {comparison.id}"
            print(msg)
            messages.add_message(request, messages.INFO, msg)
            tree = Tree(tree_type=tree_type, comparison=comparison, newick=json_response['tree'])
            tree.save()
        elif 'error' in json_response:
            msg = json_response['error']
            print(msg)
            messages.add_message(request, messages.ERROR, msg)
        elif 'job_id' in json_response:
            msg = f"job id {json_response['job_id']} neither returned a tree nor an error message."
            print(msg)
            messages.add_message(request, messages.ERROR, msg)
        else:
            raise ValueError("Error when calling Bio API")
        comparison.save()
    return HttpResponseRedirect(reverse(comparison_list))