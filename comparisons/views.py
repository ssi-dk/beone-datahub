from base64 import b64encode
from json import dumps

import requests

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.conf import settings
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.shortcuts import redirect

from bio_api.persistence.mongo import MongoAPI
from comparisons.models import Tree, Comparison, Dashboard
from comparisons.forms import NewComparisonForm, NewDashboardForm
from microreact_integration.project_assembler import assemble_project

TREE_TYPE_IDS = [ t[0] for t in Tree.TREE_TYPES ]

mongo_api = MongoAPI(settings.MONGO_CONNECTION)

def redirect_root(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/comparisons/')
    else:
        return HttpResponseRedirect('/login/')
    
@login_required
def sample_list(request):
    # TODO use entry[1] for template header line
    fields_to_get = { entry[0] for entry in settings.SAMPLE_VIEW_COLUMNS }
    samples = mongo_api.get_samples(fields=fields_to_get)
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
            if 'error' in json_response:
                msg = f"Error getting distance matrix for comparison {comparison.id}"
                messages.add_message(request, messages.ERROR, msg)
                print(msg)
                print(json_response)
                messages.add_message(request, messages.ERROR, json_response['error'])
                comparison.dm_status = "ERROR"
                comparison.save()
                return HttpResponseRedirect(reverse(comparison_list))
            else:
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
        elif comparison.dm_status == 'PENDING':
            msg = (f"There is already a pending distance matrix request for comparison {comparison.id}")
            print(msg)
            messages.add_message(request, messages.ERROR, msg)
            return HttpResponseRedirect(reverse(comparison_list))
        else:
            assert comparison.dm_status == 'VALID'  # We should only end up here in case dm_status is VALID

        # Check if we already have a Tree with the desired method for the desired Comparison
        existing = comparison.tree_set.filter(comparison=comparison.pk, tree_type=tree_type)
        if existing:
            return redirect("launchpad", tree_id=existing.first().pk)  # TODO: What if there are more than one?
        else:
            # Generate tree
            print(f"Reusing previous distance matrix for comparison {comparison.id}")
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
                msg = f"Successfully created a tree with method {tree_type} for comparison with id {comparison.id}. \n" + \
                "You can view it in Launchpad by clicking it again in the list below."
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

@login_required
def launchpad(request, tree_id):
    tree = Tree.objects.get(uuid=tree_id)
    dashboards = Dashboard.objects.filter(tree=tree.pk)
    sequences = tree.comparison.sequences
    
    if request.method == 'POST':
        form = NewDashboardForm(request.POST)
        if form.is_valid():
            dashboard = Dashboard(
                created_by=request.user,
                tree=tree,
                tbr_data_fields=form.cleaned_data['tbr_data_fields'],
                lims_data_fields=form.cleaned_data['lims_data_fields'],
            )
            msg = "Microreact is not yet integrated."
            messages.add_message(request, messages.INFO, msg)
            tbr_metadata_collection = settings.METADATA_COLLECTIONS['tbr']
            # Convert sequnce ids to isolate ids
            sample_ids_raw = mongo_api.get_samples_from_sequence_ids(sequences, ['sample_id'])
            sample_ids = [ sub['sample_id'] for sub in sample_ids_raw ]
            print("Sample ids:")
            print(list(sample_ids))
            document_count, tbr_metadata = mongo_api.get_metadata(tbr_metadata_collection, sample_ids, dashboard.tbr_data_fields)
            if document_count < len(sequences):
                msg = f"You asked for {len(sequences)} documents, but we only found {document_count}."
                messages.add_message(request, messages.WARNING, msg)
            metadata_values = list()
            first_record = next(tbr_metadata)
            metadata_keys = list(first_record.keys())
            metadata_values.append(list(first_record.values()))
            while True:
                try:
                    metadata_values.append(list(next(tbr_metadata).values()))
                except StopIteration:
                    break
            print("Matadata keys:")
            print(metadata_keys)
            print("Metadata values:")
            print(metadata_values)
            # tree_encoded = b64encode(tree.newick.encode('utf-8'))
            # tbr_metadata_str = "\n".join(tbr_metadata_list)
            # print("tbr_metadata_str:")
            # print(tbr_metadata_str)
            # tbr_metadata_encoded = b64encode(tbr_metadata_str.encode('utf-8'))
            # print("tbr metadata encoded:")
            # print(tbr_metadata_encoded)
            # print("tree encoded:")
            # print(tree_encoded)
            # TODO Repeat The code section above for lims metadata and manual metadata
            project_name = request.user.username + '_' + str(timezone.now())
            project = assemble_project(project_name, metadata_keys, metadata_values, tree)
            #TODO Access-Token must be saved per user
            access_token = 'eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..aoxg7jxHXGKS5gsU.9lcYdFeogzy9mEth0aAy3FmFucmDCAd0HVwnz5ssm3dKvY_jVkRc_UviOs0K8mimGzZBE4btSPpmh-B9rN7ba6x6Bt2aIjEuY526hxSUjzTrot6V4F0auVJOfHmtU4U106jAS2pD5kte4H51GfCRVw.35f_9LCrIg0lWpkO_Geekw'
            response = requests.post(
                f'{settings.MICROREACT_BASE_URL}/api/projects/create/',
                headers= {
                    'Content-Type': 'application/json; charset=utf-8',
                    'Access-Token': access_token
                    },
                data=dumps(project.to_dict()),
            )
            print(response)
            print(response.json())
            # TODO Create project in Microreact, get project id & url from response
            # TODO dashboard.save()
            # TODO open dashboard url in new browser tab
    else:
        form = NewDashboardForm()

    return render(request, 'comparisons/launchpad.html',{
    'form': form,
    'tree': tree,
    'sequence_count': len(tree.comparison.sequences),
    'dashboards': dashboards,
    'microreact_url': settings.MICROREACT_BASE_URL
    })