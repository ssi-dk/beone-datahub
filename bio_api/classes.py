from dataclasses import dataclass
from datetime import date

"""The purpose of these classes is to organize data in a logic and efficient way.
They have automatically generated __init__() methods as documented here:
https://docs.python.org/3/library/dataclasses.html#module-dataclasses
"""

@dataclass
class Organization:
    name: str

@dataclass
class SequencingRun:
    run_name: str
    run_date: date

@dataclass
class Sample:
    sample_id: str
    owner: Organization
    run: SequencingRun
    imported_metadata: dict  # {'tbr': ..., 'lims': ...}

@dataclass
class Sequence:
    sequence_id: str
    sample: Sample
    analysis_results: dict
    assessments: dict
