from lib2to3.pytree import Base
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

import pymongo

class Command(BaseCommand):
    help = "Add root level id's to samples in MongoDB"

    def add_arguments(self, parser):
        parser.add_argument('owning_org', type=str)

    def handle(self, *args, **options):
        print(options['owning_org'])

        connection = pymongo.MongoClient(settings.MONGO_CONNECTION)
        db = connection.get_database()
        number = db.samples.count_documents({})
        self.stdout.write(f"{str(number)} samples found.")

        new_values = { "$set": { "owning_org": options['owning_org'] } }
        # db.samples.update_many({}, new_values)
        db.samples.update_many({}, [{'$set': {'foo_new': '$owning_org'}}], False)

        self.stdout.write(self.style.SUCCESS('Success!'))