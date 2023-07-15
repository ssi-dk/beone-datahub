import random
import string

from django.core.management.base import BaseCommand
from django.conf import settings
from copy import deepcopy

from bio_api.persistence import mongo
from bio_api.persistence.bifrost_sample_template import bifrost_sample_template
from bio_api import classes


def rndstr(length):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def rndpct():
    i: int = random.randint(0, 9999)
    f: float = i / 100
    s: str = '{:.2f}'.format(f)
    return f

def allele_generator():
    locus = 31717
    while locus <= 40274:
        yield "INNU_" + str(locus)  # The locus name cannot be more than 10 chars!
        locus += 1

class Command(BaseCommand):
    help = "Generate fake samples with allele profiles in MongoDB."

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=1, help="Number of fake samples to generate.")

    def handle(self, *args, **options):

        mongo_api = mongo.MongoAPI(settings.MONGO_CONNECTION)
        self.stdout.write(f'Currently MongoDB contains {str(mongo_api.db.samples.count_documents({}))} sequences')
        run_name = rndstr(10)
        self.stdout.write(f"Fake run name: {run_name}")
        self.stdout.write(f"Will now create {options['count']} fake sequence(s)")

        for n in range(0, options['count']):

            # Create fake sequence document
            sequence = classes.Sequence(deepcopy(bifrost_sample_template))
            sequence.isolate_id = rndstr(10)
            sequence.sequence_id = run_name + '_' + sequence.isolate_id
            sequence.mongo_doc['categories']['cgmlst']['summary']['call_percent'] = rndpct()
            for locus in allele_generator():
                sequence.mongo_doc['categories']['cgmlst']['report']['data']['alleles'][locus] = str(random.randint(1, 1000))

            # Insert data in Bifrost samples collection
            result = mongo_api.db.samples.insert_one(sequence.mongo_doc)
            if result.acknowledged:
                self.stdout.write(self.style.SUCCESS(sequence.sequence_id))
            else:
                self.stdout.write(self.style.ERROR(f"Could not add sequence {sequence.sequence_id} in MongoDB!"))

            #TODO Create fake metadata documents
        
        self.stdout.write(f'MongoDB now contains {str(mongo_api.db.samples.count_documents({}))} sequences')