from dataclasses import dataclass
from datetime import date

try:
    from persistence.bifrost_sample_template import bifrost_sample_template
except ImportError:
    from bio_api.persistence.bifrost_sample_template import bifrost_sample_template

"""The purpose of these classes is to organize data in a logic and efficient way.
They have automatically generated __init__() methods as documented here:
https://docs.python.org/3/library/dataclasses.html#module-dataclasses
"""

@dataclass
class CommonMetadata:
    pass # add common metadata fields here. See both sap_lims_metadata and sap_tbr_metadata; remember there are both mandadory and optional fields

@dataclass
class SSIMetadata(CommonMetadata):
    pass # add SSI-specific metadata fields here See sap_tbr_metadata; remember there are both mandadory and optional fields

@dataclass
class FVSTMetadata(CommonMetadata):
    pass # add FVST-specific metadata fields here See sap_lims_metadata; remember there are both mandadory and optional fields

@dataclass
class Sample:
    sample_id: str

@dataclass
class SSISample(Sample):
    metadata: SSIMetadata or None

@dataclass
class FVSTSample(Sample):
    metadata: FVSTMetadata or None

@dataclass
class Assessments:
    pass  # se sap_manual_metadata

@dataclass
class Sequence:
    sequence_id: str
    sample: SSISample or FVSTSample
    categories: dict or None
    assessments: dict or None


if __name__ == "__main__":
    sample = SSISample(sample_id='sample_id_1', metadata=None)
    sequence = Sequence(
        sequence_id='sequence_id_1',
        sample=sample,
        categories=bifrost_sample_template['categories'],
        assessments=None
        )
    print(sequence.__dict__)