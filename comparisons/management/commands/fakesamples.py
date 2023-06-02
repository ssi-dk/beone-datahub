from pathlib import Path
from sys import exit
import json
from os import getcwd

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from main.models import DataSet

import pymongo

class Command(BaseCommand):
    help = "Generate fake samples with allele profiles in MongoDB."

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=1, help="Number of fake samples to generate.")

    def handle(self, *args, **options):

        connection = pymongo.MongoClient(settings.MONGO_CONNECTION)
        db = connection.get_database()
        number = db.samples.count_documents({})
        self.stdout.write(f'Currently MongoDB contains {str(number)} samples.')
        template_file = Path(getcwd(), 'comparisons', 'management', 'commands', 'fakesample_template.json')
        template = open(template_file, 'r')

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