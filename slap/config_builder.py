import os


def build_config(directories):
    services = [{'input': path_to_mxd} for path_to_mxd in get_mxds(directories)]
    config = {
        'agsUrl': 'https://<hostname>:6443/arcgis/admin',
        'mapServices': {
            'services': services
        }
    }
    return config


def get_mxds(directories):
    mxds = []
    for directory in directories:
        mxds += [
            os.path.join(directory, f)
            for root, dirs, files in os.walk(directory)
            for f in files
            if f.lower().endswith('mxd')
        ]
    return mxds
