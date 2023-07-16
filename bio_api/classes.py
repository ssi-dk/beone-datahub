class Sequence():
    sample_doc: dict = {
        "categories": {
            "contigs": {
                "summary": dict()
            },
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
                "report": dict(),
                "metadata": dict(),
                "version": dict()
            }
        }
    }

    def __init__(self, sample_doc:dict=None, imported_metadata:dict=None, manual_metadata:dict=None):
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

        if imported_metadata:
            self.imported_metadata = imported_metadata
        if manual_metadata:
            self.manual_metadata = manual_metadata

    @property
    def sequence_id(self):
        return self.sample_doc['categories']['sample_info']['summary']['sample_name']
    
    @sequence_id.setter
    def sequence_id(self, sequence_id: str):
        self.sample_doc['categories']['sample_info']['summary']['sample_name'] = sequence_id
    
    @property
    def isolate_id(self):
        return self.sample_doc['name']
    
    @isolate_id.setter
    def isolate_id(self, isolate_id: str):
        self.sample_doc['name'] = isolate_id
    
    @property
    def owner(self):
        return self.sample_doc['sample_info']['summary']['institution']
    
    @owner.setter
    def owner(self, owner: str):
        self.sample_doc['sample_info']['summary']['institution'] = owner
    
    # The properties below are (at least for now) not guaranteed to exist

    @property
    def species(self):
        return self.sample_doc['categories']['species']['detection']['summary']['detected_species']
    
    @species.setter
    def species(self, species: str):
        self.sample_doc['categories']['species']['detection']['summary']['detected_species'] = species
    
    @property
    def allele_profile(self):
        return self.sample_doc['categories']['cgmlst']['report']['data']['alleles']
    
    @allele_profile.setter
    def allele_profile(self, allele_profile: dict):
        self.sample_doc['categories']['cgmlst']['report']['data']['alleles'] = allele_profile
    
    @property
    def sequence_type(self):
        return self.sample_doc['categories']['cgmlst']['report']['data']['sequence_type']
    
    @sequence_type.setter
    def sequence_type(self, sequence_type: int):
        self.sample_doc['categories']['cgmlst']['report']['data']['sequence_type'] = sequence_type
