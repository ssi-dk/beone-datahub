from microreact_integration import classes

def stringify(value_list):
    line = ";".join([str(value) for value in value_list])
    return line + "\n"


def assemble_project(project_name: str, metadata_keys: list, metadata_values: list, tree: str):
    """
    Create an object that models a Microreact project and which can easily be used with the
    Microreact projects/create API endpoint to create a  project.

    project_name: the name that will be shown for the project
    metadata_keys: keys of the metadata fields as a list. The first one is assumed to be the id field
    metadata_values: metadata values a list of lists
    tree: tree in Newick format
    """
    project_meta = classes.Meta(name=project_name)
    id_field_name = metadata_keys[0]

    metadata_body = str()
    metadata_body += stringify(metadata_keys)  # Add keys as first line in body
    for record in metadata_values:
        metadata_body += stringify(record)

    metadata_file = classes.File(project_name=project_name, type='data', body=metadata_body)
    newick_file = classes.File(project_name=project_name, type='tree', body=tree)
    dataset = classes.Dataset(id='dataset-1', file=metadata_file.id, idFieldName=id_field_name)
    tree =  classes.Tree(
            id='tree-1',
            type='rc',
            title='Tree',
            labelField=id_field_name,
            file=newick_file.id,
            highlightedId=None
        )
    table = classes.Table(paneId='table-1', title='Metadata', columns=metadata_keys, file=metadata_file.id)

    timelines = dict()  # TODO

    project = classes.Project(
        meta=project_meta,
        datasets=[dataset],
        files=[metadata_file, newick_file],
        tables=[table],
        timelines=timelines,
        trees = [tree],
        schema="https://microreact.org/schema/v1.json"
    )

    return project
