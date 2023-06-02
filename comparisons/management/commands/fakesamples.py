from pathlib import Path
from sys import exit
import json
import random
import string
from os import getcwd

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from main.models import DataSet

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
        yield "INNUENDO_cgMLST-000" + str(locus), str(999)
        locus += 1

class Command(BaseCommand):
    help = "Generate fake samples with allele profiles in MongoDB."

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=1, help="Number of fake samples to generate.")

    def handle(self, *args, **options):

        connection = pymongo.MongoClient(settings.MONGO_CONNECTION)
        db = connection.get_database()
        number = db.samples.count_documents({})
        self.stdout.write(f'Currently MongoDB contains {str(number)} samples.')
        run_name = rndstr(10)
        self.stdout.write(f"Fake run name: {run_name}")
        template_file = Path(getcwd(), 'comparisons', 'management', 'commands', 'fakesample_template.json')
        template = open(template_file, 'r')
        sample = json.load(template)

        sample_name = rndstr(10)
        self.stdout.write(f"Short sample name: {sample_name}")
        sample['name'] = sample_name
        sample['categories']['sample_info']['summary']['sample_name'] = run_name + '_' + sample_name
        sample['categories']['cgmlst']['summary']['call_percent'] = rndpct()
        for (locus, value) in allele_generator():
            sample['categories']['cgmlst']['report']['data']['alleles'][locus] = str(random.randint(1, 1000))
        

        # folder = Path(options['folder'])
        # if not folder.exists():
        #     self.stderr.write(self.style.ERROR(f"Folder {folder} does not exist!"))
        #     exit()
        
        # p = folder.glob('*.json')
        # files = [x for x in p if x.is_file()]
        # mongo_keys = list()  # org, name key pairs to add to dataset

        # for file in files:
        #     self.stdout.write(f"Importing file {file.name}...")
        #     with open(file, 'r') as f:
        #         content = json.loads(f.read())
        #         content['org'] = options['org']
        #         content['name'] = content['sample']['summary']['sample']
        #         result = db.samples.insert_one(content)
        #         if result.acknowledged:
        #             self.stdout.write(self.style.SUCCESS(f"Org {content['org']} name {content['name']} added to MongoDB."))
        #             mongo_keys.append({'org': content['org'], 'name': content['name']})
        #         else:
        #             self.stdout.write(self.style.ERROR(f"Could not update sample in MongoDB: org: {content['org']}, name {content['name']}"))
                

        # number = db.samples.count_documents({})
        # self.stdout.write(f'After import MongoDB contains {str(number)} samples.')
        # self.stdout.write(f"Creating dataset {options['dataset']}.")
        # dataset = DataSet(
        #     species=options['sp'],
        #     name=options['dataset'],
        #     description="Imported with jsonmport",
        #     mongo_keys=mongo_keys
        #     )
        # dataset.save()
        # self.stdout.write(self.style.SUCCESS('Success!'))