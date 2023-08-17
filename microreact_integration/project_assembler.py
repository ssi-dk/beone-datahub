import classes

def assemble_project(project_name: str, metadata: str, tree: str):
    project_meta = classes.Meta(name=project_name)
    metadata_file = classes.File(project_name=project_name, type='data', body=metadata)
    newick_file = classes.File(project_name=project_name, type='tree', body=tree)
