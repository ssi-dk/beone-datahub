from pathlib import Path
from sys import exit
import json
import random
import string
from os import getcwd

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

import pymongo

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
    help = "Get at list of random sequence ids separated by spaces."

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=1, help="Number of sequence ids to get.")

    def handle(self, *args, **options):
        connection = pymongo.MongoClient(settings.MONGO_CONNECTION)
        db = connection.get_database()
        random_sequences = db.samples.aggregate([{ '$sample': { 'size': options['count'] }}])
        for s in random_sequences:
            self.stdout.write('hej')

        # for n in range(0, options['count']):
        #     with open(template_file, 'r') as template:
        #         sample = json.load(template)
        #     sample_name = rndstr(10)
        #     self.stdout.write(f"Short sample name: {sample_name}")
        #     sample['name'] = sample_name
        #     long_name = run_name + '_' + sample_name
        #     sample['categories']['sample_info']['summary']['sample_name'] = long_name
        #     sample['categories']['cgmlst']['summary']['call_percent'] = rndpct()
        #     for locus in allele_generator():
        #         sample['categories']['cgmlst']['report']['data']['alleles'][locus] = str(random.randint(1, 1000))
        #     result = db.samples.insert_one(sample)
        #     if result.acknowledged:
        #         self.stdout.write(self.style.SUCCESS(f"Sample {long_name} added to MongoDB."))
        #     else:
        #         self.stdout.write(self.style.ERROR(f"Could not add sample {long_name} in MongoDB!"))
        
        # self.stdout.write(f'MongoDB now contains {str(db.samples.count_documents({}))} samples.')