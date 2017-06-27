import os
import json


def create_config(directories, filename='config.json', hostname='hostname', register_data_sources=False):
    config = _create_config_dictionary(directories, hostname, register_data_sources)
    with open(filename, 'w+') as fp:
        json.dump(config, fp, indent=4)


def _create_config_dictionary(directories, hostname='hostname', register_data_sources=False):
    mxds = _get_mxds(directories)
    services = [{'input': path_to_mxd} for path_to_mxd in mxds]
    config = {
        'agsUrl': 'https://{}:6443/arcgis/admin'.format(hostname),
        'mapServices': {
            'services': services
        }
    }
    if register_data_sources:
        config['dataSources'] = _get_data_sources(mxds)

    return config


def _get_mxds(directories):
    return [
        os.path.join(directory, f)
        for directory in directories
        for root, dirs, files in os.walk(directory)
        for f in files
        if f.lower().endswith('mxd')
    ]


def _get_data_sources(mxds):
    from slap.esri import ArcpyHelper
    return _create_data_sources_config(ArcpyHelper.get_workspaces_with_names(mxds))


def _create_data_sources_config(data_sources):
    return [
        {
            'name': data_source['name'],
            'serverPath': data_source['workspacePath']
        }
        for data_source in data_sources
    ]
