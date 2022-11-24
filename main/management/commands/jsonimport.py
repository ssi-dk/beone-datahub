from enum import unique
from lib2to3.pytree import Base
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

import pymongo

class Command(BaseCommand):
    help = "Import sample data from BeONE JSON files."

    def add_arguments(self, parser):
        parser.add_argument('folder', type=str, help="Folder containing JSON files.")
        parser.add_argument('org', type=str, help="Acronym for the owning organization; f. ex. 'SSI'.")

    def handle(self, *args, **options):

        connection = pymongo.MongoClient(settings.MONGO_CONNECTION)
        db = connection.get_database()
        number = db.samples.count_documents({})
        self.stdout.write(f'Currently MongoDB contains{str(number)} samples.')

        self.stdout.write("Creating unique index on org+name if missing...")
        db.samples.create_index([('org', 1), ('name', 1)], unique=True)

        # For each JSON file
        # db.samples.insert_one({}, [
        #         { '$set': { 'org': options['org'] } },
        #         {'$set': {'name': '$sample.summary.sample'}}
        #     ], False)

        number = db.samples.count_documents({})
        self.stdout.write(f'After import MongoDB contains{str(number)} samples.')
        self.stdout.write(self.style.SUCCESS('Success!'))