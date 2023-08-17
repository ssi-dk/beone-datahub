from microreact_integration import classes

def assemble_project(project_name: str, metadata: str, tree: str):
    # TODO
    # We need to examine the content of the 'metadata'ø variable in order to:
    # 1. Determine the idFieldName (assumed to be the name of first column)
    # 2. Get the complete list of column names, which we need to into the 'tables' object
    idFieldName = None  # TODO
    project_meta = classes.Meta(name=project_name)
    metadata_file = classes.File(project_name=project_name, type='data', body=metadata)
    newick_file = classes.File(project_name=project_name, type='tree', body=tree)
    dataset = classes.Dataset(id='dataset-1', file=metadata_file.name, idFieldName=idFieldName)
    tree =  classes.Tree(
            type='rc',
            title='Tree',
            labelField=idFieldName,
            file=newick_file,
            highlightedId=None
        )
    tables = dict()  # TODO
    timelines = dict()  # TODO

    project = classes.Project(
        meta=project_meta,
        datasets=[dataset],
        files=[metadata_file, newick_file],
        tables=tables,
        timelines=timelines,
        trees = {"tree-1": tree},
        schema="https://microreact.org/schema/v1.json"
    )

    return project
