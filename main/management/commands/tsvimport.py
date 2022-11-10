from pathlib import Path
from sys import exit

import pymongo

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

class Command(BaseCommand):
    help = "Import allele profile and metadata from TSV files." + \
            "'folder' must be a valid path to a folder which contains two files with TSV data; " + \
            "one named like '*alleles.tsv' and the other named like '_metadata.tsv', containing" + \
            " allele profiles and metadata, respectively."

    def add_arguments(self, parser):
        parser.add_argument('folder', type=str)
        # parser.add_argument('org', type=str)
        # parser.add_argument('dataset', type=str)

    def handle(self, *args, **options):
        folder = Path(options['folder'])
        if not folder.exists():
            self.stderr.write(f"Folder {folder} does not exist!")
            exit()

        self.stdout.write(f"You selected folder {options['folder']} as input folder.")

        connection = pymongo.MongoClient(settings.MONGO_CONNECTION)
        db = connection.get_database()
        number = db.samples.count_documents({})
        self.stdout.write(f'MongoDB currently contains {str(number)} samples.')


        # for line in allele_generator:
        #     # Or maybe through API?
        #     db.samples.insert({
        #         'org': options['org'],
        #         'name': '$sample.summary.sample'
        #         # Add allele profile from allele_generator
        #         # Assert that sample name from metadata_generator == sample name from allele_generator
        #         # Add metadata from metadata_generator
        #         })

        self.stdout.write(self.style.SUCCESS('Success!'))