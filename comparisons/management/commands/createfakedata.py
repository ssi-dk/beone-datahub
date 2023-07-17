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
            sequence = classes.Sequence.from_bifrost_sample(deepcopy(bifrost_sample_template))
            sequence.isolate_id = rndstr(10)
            sequence.sequence_id = run_name + '_' + sequence.isolate_id
            sequence.sample_doc['categories']['cgmlst']['summary']['call_percent'] = rndpct()
            for locus in allele_generator():
                sequence.sample_doc['categories']['cgmlst']['report']['data']['alleles'][locus] = str(random.randint(1, 1000))

            # Insert data in Bifrost samples collection
            result = mongo_api.db.samples.insert_one(sequence.sample_doc)
            if result.acknowledged:
                self.stdout.write(self.style.SUCCESS(sequence.sequence_id))
            else:
                self.stdout.write(self.style.ERROR(f"Could not add sequence {sequence.sequence_id} in MongoDB!"))

            # Create fake metadata document
            self.stdout.write("Creating fake metadata")
            travel = random.sample(['J', 'N'], 1)[0]
            print (f"Travel: {travel}")
            if travel == 'J':
                travel_country = random.sample(['SPANIEN', 'UNITED_KINGDOM', 'GRÆKENLAND', 'BULGARIEN', 'TYRKIET'], 1)[0]
            else:
                travel_country = None
            print(travel_country)
            tbr_doc = {
                'isolate_id': sequence.isolate_id,
                'age': random.randint(0, 100),
                'gender': random.sample(['K', 'M'], 1)[0],
                'kma': random.sample(['Rigshospitalet', 'OUH', 'Herlev', 'Hvidovre', 'Aalborg', 'Skejby'], 1)[0],
                'region': random.sample(['SYDDANMARK', 'MIDTJYLLAND', 'SJÆLLAND', 'HOVEDSTADEN', 'NORDJYLLAND'], 1)[0],
                'travel': travel,
                'travel_country': travel_country,
                'primary_isolate': True,
            }
            print(tbr_doc)

            # Insert data in TBR metadata collection
            result = mongo_api.db.sap_tbr_metadata.insert_one(tbr_doc)
            if result.acknowledged:
                self.stdout.write(self.style.SUCCESS(tbr_doc['isolate_id']))
            else:
                self.stdout.write(self.style.ERROR(f"Could not add TBR metadata for isolate {tbr_doc['isolate_id']} in MongoDB!"))
        
        self.stdout.write(f'MongoDB now contains {str(mongo_api.db.samples.count_documents({}))} sequences')