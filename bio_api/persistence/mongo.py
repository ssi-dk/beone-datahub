import re
import pymongo
from bson.objectid import ObjectId
from datetime import date

#TODO Make this a configurable item somehow.
SEQUENCE_FIELD_MAPPING: dict = {
    'owner': 'categories.sample_info.summary.institution',
    'sequence_id': 'categories.sample_info.summary.sample_name',
    'sample_id': 'name',
    'species': 'categories.species_detection.summary.detected_species',
    'allele_profile': 'categories.cgmlst.report.data.alleles',
    'sequence_type': 'categories.cgmlst.report.data.sequence_type'
}

# Handy shortcuts when importing JSON data into Python code
true = True
false = False
null = None

def BinData(integer, string):
    """"Dummy function - can be used when importing a MongoDB document as a hardcoded Python dict"""
    return string

def ISODate(date_str: str):
    """"Can be used when importing a MongoDB document as a hardcoded dict in Python.
    Input format: 2020-01-04T13:03:00Z"""
    return date(date_str)


def get_sequence_id(structure: dict):
    return structure['categories']['sample_info']['summary']['sample_name']


def get_alleles(structure: dict):
    return structure['categories']['cgmlst']['report']['data']['alleles'] 


class MongoAPIError(Exception):
    pass


class MongoAPI:
    def __init__(self, connection_string: str, field_mapping: dict=SEQUENCE_FIELD_MAPPING):
        self.connection = pymongo.MongoClient(connection_string)
        self.db = self.connection.get_database()
        self.field_mapping = field_mapping

    # Get samples from MongoDB object ids
    def get_samples(
        self,
        mongo_ids = None,
        species_name: str = None,
        fields: set = set(SEQUENCE_FIELD_MAPPING.keys())
    ):
        pipeline = list()

        # Match
        match = dict()
        if mongo_ids:
            object_ids = [ObjectId(mongo_id) for mongo_id in mongo_ids]
            match['_id'] = { '$in': object_ids }
        species_field = SEQUENCE_FIELD_MAPPING['species']
        if species_name:
            match[species_field ] = species_name

        pipeline.append(
            {'$match': match}
        )

        # Projection
        projection = dict()
        for field in fields:
            if isinstance(SEQUENCE_FIELD_MAPPING[field], str):
                projection[field] = f"${SEQUENCE_FIELD_MAPPING[field]}"
            else:
                projection[field] = SEQUENCE_FIELD_MAPPING[field]

        pipeline.append(
            {'$project': projection
            }
        )

        return self.db.samples.aggregate(pipeline)


    def get_samples_from_sequence_ids(
        self,
        sid_list:list,
        fields: set = set(SEQUENCE_FIELD_MAPPING.keys())
    ):

        pipeline = list()
        sid_field = SEQUENCE_FIELD_MAPPING['sequence_id']

        # Match
        pipeline.append(
            {'$match':
                {
                    sid_field: {'$in': sid_list}
                }
            }
        )
        
        # Projection - map only the desired fields
        projection = dict()
        for field in fields:
            if isinstance(SEQUENCE_FIELD_MAPPING[field], str):
                projection[field] = f"${SEQUENCE_FIELD_MAPPING[field]}"
            else:
                projection[field] = SEQUENCE_FIELD_MAPPING[field]
        
        pipeline.append(
            {'$project': projection
            }
        )

        return self.db.samples.aggregate(pipeline)

    def get_sequences(self, sequence_ids:list):
        # Get sequences from sequence ids
        list_length = len(sequence_ids)
        sequence_id_field = SEQUENCE_FIELD_MAPPING['sequence_id']
        query = {sequence_id_field: {'$in': sequence_ids}}
        document_count = self.db.samples.count_documents(query)
        if list_length != document_count:
            raise MongoAPIError (f"You asked for {list_length} documents, but the number of matching documents is {document_count}.")
        return self.db.samples.find(query)
    
    def get_metadata(
        self,
        collection: str,
        isolate_ids: list,
        fields
    ):
        # Get metadata from isolate ids
        # Note: 'isolate' is the appropriate term here as metadata relate to isolates, not sequences
        list_length = len(isolate_ids)
        print(isolate_ids)
        query = {'isolate_id': {'$in': isolate_ids}}
        document_count = self.db[collection].count_documents(query)
        mongo_cursor = self.db[collection].find(query)
        print(list(mongo_cursor))
        if document_count > len(isolate_ids):  # document_count < list length is OK since not all isolates might have metadata!
            raise MongoAPIError (f"Too many documents: You asked for {list_length} documents, but the number of matching documents is {document_count}.")
        return document_count, mongo_cursor