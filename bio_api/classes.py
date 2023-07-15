from dataclasses import dataclass
from datetime import date

try:
    from persistence.bifrost_sample_template import bifrost_sample_template
except ImportError:
    from bio_api.persistence.bifrost_sample_template import bifrost_sample_template


class MongoDocument:
    def __init__(self, mongo_doc: dict):
        self.mongo_doc = mongo_doc


class Sequence(MongoDocument):
    def __init__(self, bifrost_sample_doc, imported_metadata:dict=None, manual_metadata:dict=None):
        super(Sequence).__init__(bifrost_sample_doc)
        try:
            assert 'sample_name' in self.mongo_doc['categories']['sample_info']
        except AssertionError, KeyError:
            raise ValueError("sample_name not found")
        try:
            assert 'name' in self.mongo_doc
        except AssertionError:
            raise ValueError("name not found")
        try:
            assert 'institution' in self.mongo_doc['sample_info']['summary']
        except AssertionError, KeyError:
            raise ValueError("institution not found")

        if imported_metadata:
            self.imported_metadata = imported_metadata
        if manual_metadata:
            self.manual_metadata = manual_metadata

    @property
    def sequence_id(self):
        return self.mongo_doc['categories']['sample_info']['sample_name']
    
    @property
    def isolate_id(self):
        return self.mongo_doc['name']
    
    @property
    def owner(self):
        return self.mongo_doc['sample_info']['summary']['institution']
