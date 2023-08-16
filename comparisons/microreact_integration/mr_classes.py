from dataclasses import dataclass

@dataclass
class Meta:
    name: str
    # description: str

@dataclass
class Dataset:
    id: str
    file: str
    idFieldName: str

class File:
    blob: str
    format: str
    id: str
    name: str
    type: str

    def __init__(self, type, body):
        pass

    def to_blob(self):
        pass

@dataclass
class Column:
    field: str
    fixed: bool

@dataclass
class Table:
    title: str
    columns: list

@dataclass
class Timeline:
    bounds: None
    controls: False
    nodeSize: 14
    playing: False
    speed: 1
    laneField: None
    unit: None
    viewport: None
    style: str = "bar"
    title: str = "Timeline"
    dataType: str = "year-month-day"
    yearField: str = "Year"

@dataclass
class Tree:
    file: File
    type: str = "rc"
    title: str = "Tree"
    labelField: str = "Key"  # Det var derfor, jeg ikke fik labels på nodes!
    highlightedId: str = None

@dataclass
class Project:
    """Main class for structuring data that will be sent to Microreact when creating a new project.
    Use the built-in asdict method to convert data to a dict which in turn can be converted to JSON."""
    meta: Meta
    datasets: list
    files: list
    tables: list
    timelines: list
    trees: list
    schema: str