import re
import pymongo
from bson.objectid import ObjectId

from django.conf import settings


FIELD_MAPPING: dict = settings.MONGO_FIELD_MAPPING
NEW_FIELD_MAPPING: dict = settings.NEW_MONGO_FIELD_MAPPING
# Refer all hard-coded Mongo fields here so we fail immediately if a field is not defined in settings.py
HARDCODED_MONGO_FIELDS = {
    'org',
    'name',
    'species',
    'metadata',
    'sequence_type',
    'country',
    'source_type'
}
FIELDS = dict()
for field_name in HARDCODED_MONGO_FIELDS:
    assert field_name in NEW_FIELD_MAPPING
    raw_field: list = NEW_FIELD_MAPPING[field_name]
    elements = list()
    for part in raw_field:
        if isinstance(part, str):
            elements.append(part)
        elif isinstance(part, tuple):
            assert isinstance(part[0], str) or isinstance(part[0], tuple)
            assert isinstance(part[1], int)
            elements.append({ '$arrayElemAt': [ part[0], part[1] ] })
            pass
        else:
            raise ValueError()
    # print(elements)

class API:
    def __init__(self, connection_string: str, field_mapping: dict):
        self.connection = pymongo.MongoClient(connection_string)
        self.db = self.connection.get_database()
        self.field_mapping = field_mapping

    def get_samples(
        self,
        mongo_ids = None,
        species_name: str = None,
        fields: set = {'metadata', 'sequence_type', 'country_root', 'source_type_root'}
    ):

        # Ensure we always have these two fields in the set
        fields.add('org')
        fields.add('name')

        pipeline = list()

        # Match
        match = dict()
        if mongo_ids:
            object_ids = [ObjectId(mongo_id) for mongo_id in mongo_ids]
            match['_id'] = { '$in': object_ids }
        species_field = FIELD_MAPPING['species']
        if species_name:
            match[species_field ] = species_name

        pipeline.append(
            {'$match': match}
        )

        # Projection
        projection = dict()
        for field in fields:
            projection[field] = f"${FIELD_MAPPING[field]}"
        
        # Get more convenient access to some deeply nested fields
        if 'country_root' in projection:
            projection['country'] = { '$arrayElemAt': [ { '$arrayElemAt': [ projection['country_root'], 0 ] }, 0 ] }
        if 'source_type_root' in projection:
            projection['source_type'] = { '$arrayElemAt': [ { '$arrayElemAt': [ projection['source_type_root'], 0 ] }, 1 ] }
        print(projection)

        pipeline.append(
            {'$project': projection
            }
        )

        return self.db.samples.aggregate(pipeline)


    def get_samples_from_keys(
        self,
        key_list:list[dict],
        fields: set = {'metadata', 'sequence_type', 'country_root', 'source_type_root'}
    ):

        # We cannot search on an empty key_list.
        if len(key_list) == 0:
            return [list(), list()]

        # Ensure we always have these two fields in the set
        fields.add('org')
        fields.add('name')

        pipeline = list()

        # Match
        pipeline.append(
                {'$match': {'$or': key_list}}
        )

        # Projection
        projection = dict()
        for field in fields:
            projection[field] = f"${FIELD_MAPPING[field]}"
        
        # Get more convenient access to some deeply nested fields
        if 'country_root' in projection:
            projection['country'] = { '$arrayElemAt': [ { '$arrayElemAt': [ projection['country_root'], 0 ] }, 0 ] }
        if 'source_type_root' in projection:
            projection['source_type'] = { '$arrayElemAt': [ { '$arrayElemAt': [ projection['source_type_root'], 0 ] }, 1 ] }
        
        pipeline.append(
            {'$project': projection
            }
        )

        command_cursor = self.db.samples.aggregate(pipeline)

        # Check if there are samples in key_list that was not found in MongoDB.
        unmatched = list()
        for key_pair in key_list:
            match = False
            for mongo_doc in command_cursor:
                if mongo_doc['org'] == key_pair['org'] and mongo_doc['name'] == key_pair['name']:
                    match = True
                    break
            if match == False:
                unmatched.append(key_pair)

        # MongoDB CommandCursor cannot rewind, so we make a new one
        return (self.db.samples.aggregate(pipeline), unmatched)
