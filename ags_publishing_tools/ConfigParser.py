import os
import json


class ConfigParser:

    config = None
    cwd = None
    service_types = ['mapServices', 'gpServices', 'imageServices']
    required_keys = ['input', 'agsUrl']
    map_service_default_json = {
        # "serviceName": "name",
        # "description": "description",
        "type": "MapServer",
        "capabilities": "Map,Query,Data",
        "properties": {
            # "filePath": "c:\\data\\Beirut\\Beirut_Parcels.msd",
            "outputDir": "c:\\arcgisserver\\directories\\arcgisoutput",
            "virtualOutputDir": "/rest/directories/arcgisoutput"
        },
        "extensions": [
            {
                "typeName": "KmlServer",
                "enabled": True,
                "capabilities": "SingleImage,SeparateImages,Vectors",
                "properties": {
                  "minRefreshPeriod": "30",
                  "compatibilityMode": "GoogleEarth",
                  "imageSize": "1024",
                  "dpi": "96",
                  "endPointURL": "",
                  "featureLimit": "1000000",
                  "useDefaultSnippets": "false"
                }
            }
        ],
        "datasets": []
    }

    def __init__(self):
        # ESRI's tools will change the cwd, so set it at the beginning
        self.cwd = os.getcwd()

    def load_config(self, path_to_config):
        with open(path_to_config) as config_file:
            config = json.load(config_file)
        return self.parse_config(config)

    def parse_config(self, config):
        parsed = self.get_root_keys(config)
        for service_type in self.service_types:
            parsed[service_type] = self.update_keys(config, service_type)
        return parsed

    def update_keys(self, config, service_type):
        copy = {'services': []}
        if service_type in config:
            copy = config[service_type].copy()
            for service in copy['services']:
                service = reduce(self.merge, [service, self.get_root_keys(config), self.get_type_keys(config, service_type)])
        return copy

    def get_root_keys(self, config):
        root_keys = {}
        for key in config:
            if key not in self.service_types:
                root_keys[key] = config[key]
        return root_keys

    def get_type_keys(self, config, service_type):
        type_keys = {}
        for key in config:
            if key == service_type:
                for type_key in config[key]:
                    if type_key not in ['services']:
                        type_keys[type_key] = config[key][type_key]
        return type_keys

    def merge(self, a, b, path=None):
        if path is None: path = []
        for key in b:
            if key in a:
                if isinstance(a[key], dict) and isinstance(b[key], dict):
                    self.merge(a[key], b[key], path + [str(key)])
                elif a[key] == b[key]:
                    pass # same leaf value
                else:
                    a[key] = b[key]  # Always overwrite
            else:
                a[key] = b[key]
        return a

    def get_full_path(self, config_path):
        return config_path if os.path.isabs(config_path) else os.path.join(self.cwd, config_path)

    def check_required_keys(self):
        for key in self.required_keys:
            test = self.config[key]

    def get_map_service_json(self, config, server_input_path, filename):
        default_json = self.map_service_default_json.copy()
        msd_path = ConfigParser.get_msd_path(server_input_path, filename)
        default_json['properties']['filePath'] = msd_path
        json = config['json'].copy() if 'json' in config else {}
        if 'serviceName' not in config:
            json['serviceName'] = filename
        return self.merge(default_json, json)

    @staticmethod
    def get_msd_path(server_input_path, filename):
        return os.path.join(server_input_path, filename + '.MapServer', 'extracted', 'v101', filename + '.msd')