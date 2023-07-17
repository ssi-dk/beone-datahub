try:
    from persistence.bifrost_sample_template import bifrost_sample_template
except ImportError:
    from bio_api.persistence.bifrost_sample_template import bifrost_sample_template

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

    @classmethod
    def from_bifrost_sample(cls, sample_doc:dict):
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
        instance = cls()
        instance.sample_doc = sample_doc
        return instance

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


class TBRMeta:
    def __init__(self, tbr_doc: dict):
        self.age = tbr_doc.get('age')
        self.gender = tbr_doc.get('gender')
        self.kma = tbr_doc.get('kma')
        self.region = tbr_doc.get('region')
        self.travel = tbr_doc.get('travel')
        self.travel_country = tbr_doc.get('travel_country')
        self.primary_isolate = tbr_doc.get('primary_isolate')


class LIMSMeta:
    def __init__(self, lims_doc: dict):
        self.product_type = lims_doc.get('product_type')
        self.product = lims_doc.get('product')
        self.origin_country = lims_doc.get('origin_country')
        self.cvr_number = lims_doc.get('cvr_number')
        self.chr_number = lims_doc.get('chr_number')
        self.aut_number = lims_doc.get('aut_number')
        self.animal_species = lims_doc.get('animal_species')


if __name__ == '__main__':
    print("The next line show the field_mapping attribute of the Sequence class:")
    print(Sequence.field_mapping)
    print("Now we instantiate a Sequence without any arguments to the constructor.")
    sequence = Sequence()
    print("The newly created Sequence instance currently looks like:")
    print(sequence.as_dict())
    print("Now we set the sequence_id and print it.")
    sequence.sequence_id = 'test_sequence_id'
    print(sequence.sequence_id)
    print("Now we set isolate_id and print it.")
    sequence.isolate_id = 'test_isolate_id'
    print(sequence.isolate_id)
    print("Now we set owner and print it.")
    sequence.owner = 'test_sequence_owner'
    print(sequence.owner)
    print("Now we set species and print it.")
    sequence.species = 'test_sequence_species'
    print(sequence.species)
    print("Now we set sequence_type and print it.")
    sequence.sequence_type = 11
    print(sequence.sequence_type)
    print("Now we print the whole Sequence again as a dict")
    print(sequence.as_dict())
    print()
    print("Next, we'll create a Sequence from a sample dict.")
    sequence = Sequence.from_bifrost_sample(sample_doc=bifrost_sample_template)
    print(sequence.as_dict())
