from enum import unique
from lib2to3.pytree import Base
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

import pymongo

class Command(BaseCommand):
    help = "Import allele profile and metadata from TSV files." + \
            "'folder' must be a valid path to a folder which contains two files with TSV data; " + \
            "one named like '*alleles.tsv' and the other named like '_metadata.tsv', containing" + \
            " allele profiles and metadata, respectively."

    def add_arguments(self, parser):
        parser.add_argument('folder', type=str)

    def handle(self, *args, **options):
        print(options['folder'])

        connection = pymongo.MongoClient(settings.MONGO_CONNECTION)
        db = connection.get_database()
        number = db.samples.count_documents({})
        self.stdout.write(f'MongoDB currently contains {str(number)} samples.')

        # Open allele profile file and make an iterator/generator stuff thingy.
        allele_profile_file = "My allele profile file"
        allele_generator = "My allele generator thingy"

        # Also open metadata file
        metadata_file = "My metadata file"
        metadata_generator_thingy = "My metadata generator thingy"

        for line in allele_generator:
            # Or maybe through API?
            db.samples.insert({
                'org': options['org'],
                'name': '$sample.summary.sample'
                # Add allele profile from allele_generator
                # Assert that sample name from metadata_generator == sample name from allele_generator
                # Add metadata from metadata_generator
                })

        self.stdout.write(self.style.SUCCESS('Success!'))