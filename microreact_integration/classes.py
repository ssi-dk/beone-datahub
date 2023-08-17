from base64 import b64encode

from dataclasses import dataclass

@dataclass
class Meta:
    name: str
    # description: str

    def to_dict(self):
        return {'name': self.name}

@dataclass
class Dataset:
    id: str
    file: str
    idFieldName: str

class File:
    id: str
    type: str
    name: str
    format: str
    mimetype: str
    body: str

    def __init__(self, project_name, type, body):
        if type == 'data':
            self.id = project_name + '_metadata'
            self.name = project_name + '_metadata.csv'
            self.format = 'text/csv'
            self.mimetype = 'data:application/vnd.ms-excel;base64'
        elif type == 'tree':
            self.id = project_name + '_tree'
            self.name = project_name + '_tree.nwk'
            self.format = 'text/x-nh'
            self.mimetype = 'data:application/octet-stream;base64'
        else:
            raise ValueError("Invalid file type: " + type)
        self.type = type
        self.body = body
    
    def __to_dict__(self):
        blob = b64encode(self.body.encode('utf-8'))
        return {
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "format": self.format,
            "blob": self.mimetype + ',' + blob
        }

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

    def to_dict(self):
        return {
            'meta': self.meta.to_dict()
        }