from enum import unique
from lib2to3.pytree import Base
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

import pymongo

class Command(BaseCommand):
    help = "Add root level names and org's to ALL samples in MongoDB. Use with care!"

    def add_arguments(self, parser):
        parser.add_argument('org', type=str)

    def handle(self, *args, **options):
        print(options['org'])

        connection = pymongo.MongoClient(settings.MONGO_CONNECTION)
        db = connection.get_database()
        number = db.samples.count_documents({})
        self.stdout.write(f'{str(number)} samples found.')

        db.samples.update_many({}, [
                { '$set': { 'org': options['org'] } },
                {'$set': {'name': '$sample.summary.sample'}}
            ], False)
        
        db.samples.create_index([('org', 1), ('name', 1)], unique=True)

        self.stdout.write(self.style.SUCCESS('Success!'))