import os
import json


def create_config(directories, filename='config.json'):
    config = create_config_dictionary(directories)
    with open(filename, 'w') as fp:
        json.dump(config, fp)


def create_config_dictionary(directories):
    services = [{'input': path_to_mxd} for path_to_mxd in get_mxds(directories)]
    config = {
        'agsUrl': 'https://<hostname>:6443/arcgis/admin',
        'mapServices': {
            'services': services
        }
    }
    return config


def get_mxds(directories):
    return [
        os.path.join(directory, f)
        for directory in directories
        for root, dirs, files in os.walk(directory)
        for f in files
        if f.lower().endswith('mxd')
    ]
