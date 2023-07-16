class Sequence():
    sample_doc: dict = {
        "categories": {
            "species_detection": {
                "summary": dict()
            },
            "sample_info": {
                "summary": dict()
            },
            "cgmlst": {
                "name": "cgmlst",
                "component": dict(),
                "summary": dict(),
                "report": {
                    "data": dict()
                    },
                "metadata": dict(),
                "version": dict()
            }
        }
    }

    field_mapping: dict = {
        'owner': ['categories', 'sample_info', 'summary', 'institution'],
        'sequence_id':['sample_info', 'summary', 'sample_name'],
        'sample_id': ['name'],
        'species': ['species_detection', 'summary', 'detected_species'],
        'allele_profile': ['cgmlst', 'report', 'data', 'alleles'],
        'sequence_type': ['cgmlst', 'report', 'data', 'sequence_type'],
        }

    def as_dict(self):
        return self.sample_doc

    def __init__(self, sample_doc:dict=None):
        if sample_doc:
            try:
                assert 'name' in sample_doc
            except AssertionError:
                raise ValueError("name not found")
            try:
                assert 'sample_name' in sample_doc['categories']['sample_info']['summary']
            except (AssertionError, KeyError):
                raise ValueError("sample_name not found")
            try:
                assert 'institution' in sample_doc['categories']['sample_info']['summary']
            except (AssertionError, KeyError):
                raise ValueError("institution not found")
            self.sample_doc = sample_doc

    @property
    def sequence_id(self):
        try:
            return self.sample_doc['categories']['sample_info']['summary']['sample_name']
        except KeyError:
            return None
    
    @sequence_id.setter
    def sequence_id(self, sequence_id: str):
        self.sample_doc['categories']['sample_info']['summary']['sample_name'] = sequence_id
    
    @property
    def isolate_id(self):
        try:
            return self.sample_doc['name']
        except KeyError:
            return None
    
    @isolate_id.setter
    def isolate_id(self, isolate_id: str):
        self.sample_doc['name'] = isolate_id
    
    @property
    def owner(self):
        try:
            return self.sample_doc['categories']['sample_info']['summary']['institution']
        except KeyError:
            return None
    
    @owner.setter
    def owner(self, owner: str):
        self.sample_doc['categories']['sample_info']['summary']['institution'] = owner
    
    @property
    def species(self):
        try:
            return self.sample_doc['categories']['species_detection']['summary']['detected_species']
        except KeyError:
            return None

    @species.setter
    def species(self, species: str):
        self.sample_doc['categories']['species_detection']['summary']['detected_species'] = species
    
    @property
    def allele_profile(self):
        try:
            return self.sample_doc['categories']['cgmlst']['report']['data']['alleles']
        except KeyError:
            return None

    @allele_profile.setter
    def allele_profile(self, allele_profile: dict):
        self.sample_doc['categories']['cgmlst']['report']['data']['alleles'] = allele_profile
    
    @property
    def sequence_type(self):
        try:
            return self.sample_doc['categories']['cgmlst']['report']['data']['sequence_type']
        except KeyError:
            return None
    
    @sequence_type.setter
    def sequence_type(self, sequence_type: int):
        self.sample_doc['categories']['cgmlst']['report']['data']['sequence_type'] = sequence_type


if __name__ == '__main__':
    print("The next line show the field_mapping attribute of the Sequence class:")
    print(Sequence.field_mapping)
    sequence = Sequence()
    print(sequence.as_dict())
    sequence.sequence_id = 'test_sequence_id'
    print(sequence.sequence_id)
    sequence.isolate_id = 'test_isolate_id'
    print(sequence.isolate_id)
    sequence.owner = 'test_sequence_owner'
    print(sequence.owner)
    sequence.species = 'test_sequence_species'
    print(sequence.species)
    sequence.allele_profile = {'test': 'allele_profile'}
    print(sequence.allele_profile)
    sequence.sequence_type = 11
    print(sequence.sequence_type)
    print(sequence.as_dict())
