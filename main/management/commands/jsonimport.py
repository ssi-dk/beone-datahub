from pathlib import Path
from sys import exit
import json

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

import pymongo

class Command(BaseCommand):
    help = "Import sample data from BeONE JSON files."

    def add_arguments(self, parser):
        parser.add_argument('folder', type=str, help="Folder containing JSON files.")
        parser.add_argument('org', type=str, help="Acronym for the owning organization; f. ex. 'SSI'.")
        parser.add_argument('sp', type=str, help="Species shortform, for ex. 'salmonella'.")
        parser.add_argument('dataset', type=str, help="A name for the dataset (must not already exist).")

    def handle(self, *args, **options):

        connection = pymongo.MongoClient(settings.MONGO_CONNECTION)
        db = connection.get_database()
        number = db.samples.count_documents({})
        self.stdout.write(f'Currently MongoDB contains{str(number)} samples.')

        self.stdout.write("Creating unique index on org+name if missing...")
        db.samples.create_index([('org', 1), ('name', 1)], unique=True)

        folder = Path(options['folder'])
        if not folder.exists():
            self.stderr.write(self.style.ERROR(f"Folder {folder} does not exist!"))
            exit()
        
        p = folder.glob('*.json')
        files = [x for x in p if x.is_file()]

        for file in files:
            self.stdout.write(f"Importing file {file.name}...")
            with open(file, 'r') as f:
                content = json.loads(f.read())
                content['org'] = options['org']
                content['name'] = content['sample']['summary']['sample']
                result = db.samples.insert_one(content)
                if result.acknowledged:
                    self.stdout.write(self.style.SUCCESS(f"Org {content['org']} name {content['name']} added to MongoDB."))
                else:
                    self.stdout.write(self.style.ERROR(f"Could not update sample in MongoDB: org: {content['org']}, name {content['name']}"))
                

        number = db.samples.count_documents({})
        self.stdout.write(f'After import MongoDB contains {str(number)} samples.')
        self.stdout.write(self.style.SUCCESS('Success!'))