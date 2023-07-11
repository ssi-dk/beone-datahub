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
        random_sequences = db.samples.aggregate([
            {'$sample': { 'size': options['count'] }},
            {'$project' : { '_id' : 0, 'categories.sample_info.summary.sample_name': 1}}
            ])
        ids = list()
        for s in random_sequences:
            ids.append(s['categories']['sample_info']['summary']['sample_name'])
        self.stdout.write(' '.join(ids))