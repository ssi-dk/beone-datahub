from dataclasses import dataclass
from datetime import date

from persistence.bifrost_sample_template import bifrost_sample_template

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
    metadata: SSIMetadata

@dataclass
class FVSTSample(Sample):
    metadata: FVSTMetadata

@dataclass
class AnalysisResults:
    categories: dict

@dataclass
class Assessments:
    pass  # se sap_manual_metadata

@dataclass
class Sequence:
    sequence_id: str
    sample: SSISample or FVSTSample
    analysis_results: dict or None
    assessments: dict or None


if __name__ == "__main__":
    metadata = SSIMetadata()
    sample = SSISample(sample_id=bifrost_sample_template['name'], metadata=metadata)
    analysis_results = AnalysisResults(categories=bifrost_sample_template['categories'])
    assessments = Assessments()
    sequence = Sequence(
        sequence_id='sequence_id_1',
        sample=sample,
        analysis_results=analysis_results,
        assessments=assessments
        )
    print(type(sequence))
    print(sequence)