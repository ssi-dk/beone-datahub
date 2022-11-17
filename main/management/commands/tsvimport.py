from pathlib import Path
from sys import exit
from collections import OrderedDict

import pymongo

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from main.models import DataSet

all_species = { short:long for short, long in settings.ALL_SPECIES }

def dots2dicts(dot_str: str, value):
    """Helper function that converts a string with dotted notation to a recursive structure of dicts
    """
    keys: list = dot_str.split('.')
    new_dict = current = {}
    counter = 1
    for name in keys:
        if counter == len(keys):
            current[name] = value
        else:
            current[name] = {}
            current = current[name]
        counter += 1
    return new_dict

def merge_dictionaries(dict1, dict2):
    """
    Recursive merge dictionaries.

    :param dict1: Base dictionary to merge.
    :param dict2: Dictionary to merge on top of base dictionary.
    :return: Merged dictionary
    """
    for key, val in dict1.items():
        if isinstance(val, dict):
            dict2_node = dict2.setdefault(key, {})
            merge_dictionaries(val, dict2_node)
        else:
            if key not in dict2:
                dict2[key] = val

    return dict2

class Command(BaseCommand):
    help = "Import allele profile and metadata from TSV files." + \
            "'folder' must be a valid path to a folder which contains two files with TSV data; " + \
            "one named like 'alleles.tsv' and the other named like 'metadata.tsv', containing " + \
            "allele profiles and metadata, respectively." + \
            "The headers in metadata.tsv must have identical entries in settings.MONGO_FIELD_MAPPING." + \
            "The species shortform argument must match an entry in ALL_SPECIES in settings.py."

    def add_arguments(self, parser):
        parser.add_argument('folder', type=str, help="Folder containing alleles.tsv and metadata.tsv")
        parser.add_argument('org', type=str, help="Organization which these samples belong to")
        parser.add_argument('sp', type=str, help="Species shortform")
        parser.add_argument('dataset', type=str, help="A name for the dataset (must not already exist)")

    def handle(self, *args, **options):
        folder = Path(options['folder'])
        if not folder.exists():
            self.stderr.write(f"Folder {folder} does not exist!")
            exit()
        a_path = Path(folder, 'alleles.tsv')
        if not a_path.exists():
            self.stderr.write(f"File {a_path} does not exist!")
            exit()
        m_path = Path(folder, 'metadata.tsv')    
        if not m_path.exists():
            self.stderr.write(f"File {m_path} does not exist!")
            exit()

        self.stdout.write(f"You selected folder {options['folder']} as input folder.")

        connection = pymongo.MongoClient(settings.MONGO_CONNECTION)
        db = connection.get_database()
        number = db.samples.count_documents({})
        self.stdout.write(f'MongoDB currently contains {str(number)} samples (before import).')

        with open(a_path) as a_file, open(m_path) as m_file:
            a_header_list = a_file.readline().strip().split('\t')
            a_header_list.pop(0)  # First item is useless; throw away
            m_header_list = m_file.readline().strip().split('\t')
            m_header_list.pop(0)  # Useless item; throw away

            # Map metadata headers to Mongo fields
            mapping = OrderedDict()  # Or maybe just a dict?
            for header in m_header_list:
                try:
                    field = settings.MONGO_FIELD_MAPPING[header]
                    mapping[header] = field
                    self.stdout.write(f"Header '{header}' maps to {field}")
                except KeyError:
                    mapping[header] = None
                    self.stdout.write(self.style.WARNING(f"WARNING: Header '{header}' was not found in settings.MONGO_FIELD_MAPPING."))

            field_list = list(mapping.values())
            sample_count = 0
            mongo_keys = list()  # org, name key pairs to add to dataset
            while True:  # As long as there are more sample lines to read
                a_line = a_file.readline().strip()
                if not a_line:
                    self.stdout.write(f"No more lines in allele file. I have read {sample_count} lines.")
                    break
                m_line = m_file.readline().strip()
                if not m_line:
                    self.stdout.write(f"No more lines in metadata file. I have read {sample_count} lines.")
                    break
                a_list = a_line.split('\t')
                a_name = a_list.pop(0)
                m_list = m_line.split('\t')
                m_name = m_list.pop(0)
                assert a_name == m_name
                self.stdout.write(f"Importing sample {a_name}...")

                # Create document in MongoDB, using data items from both m_list and a_list
                sample_dict = {
                        'org': options['org'],
                        'name': a_name,
                        'sample': {'metadata': {'Microorganism': all_species[options['sp']]}}
                    }
                for header_number in range(0, len(mapping.keys())):
                    field = field_list[header_number]
                    print(f"Adding metadata field: {field}")
                    if field is not None:
                        dicts_to_add = dots2dicts(field, m_list[header_number])
                        sample_dict = merge_dictionaries(sample_dict, dicts_to_add)

                result = db.samples.insert_one(sample_dict)
                if not result.acknowledged:
                     self.stdout.write(self.style.ERROR(f"Could not update sample in MongoDB: org: {sample_dict}"))
                     exit
                self.stdout.write(self.style.SUCCESS(f"Sample added to MongoDB: org: {sample_dict}"))
                mongo_keys.append({'org': sample_dict['org'], 'name': sample_dict['name']})
                sample_count += 1

        number = db.samples.count_documents({})
        self.stdout.write(f'MongoDB now contains {str(number)} samples (after import).')

        # Create dataset
        dataset = DataSet(
            species=options['sp'],
            name=options['dataset'],
            description="Imported with tsvimport",
            mongo_keys=mongo_keys
            )
        dataset.save()
        self.stdout.write(self.style.SUCCESS(f"Created dataset:  {options['dataset']}"))