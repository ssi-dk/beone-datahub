from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

import pymongo

class Command(BaseCommand):
    help = "Add root level id's to samples in MongoDB"

    def add_arguments(self, parser):
        parser.add_argument('owning_org', type=str)

    def handle(self, *args, **options):
        connection = pymongo.MongoClient(settings.MONGO_CONNECTION)
        db = connection.get_database()
        samples = db.samples.find({})
        self.stdout.write(self.style.SUCCESS('Success!'))