import os
import json

class ConfigParser:

    config = None
    types = ['mapServices', 'gpServices', 'imageServices']
    required_keys = ['input', 'connectionFilePath']

    def __init__(self):
        pass

    def load_config(self, path_to_config):
        with open(path_to_config) as config_file:
            config = json.load(config_file)
        return self.parse_config(config)

    def parse_config(self, config):
        parsed = {}
        for type in self.types:
            parsed[type] = self.update_keys(config, type)
        return parsed

    def update_keys(self, config, type):
        copy = {'services': []}
        if type in config:
            copy = config[type].copy()
            for service in copy['services']:
                service = reduce(self.merge, [service, self.get_root_keys(config), self.get_type_keys(config, type)])
        return copy

    def get_root_keys(self, config):
        root_keys = {}
        for key in config:
            if key not in self.types:
                root_keys[key] = config[key]
        return root_keys

    def get_type_keys(self, config, type):
        type_keys = {}
        for key in config:
            if key == type:
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
                    raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
            else:
                a[key] = b[key]
        return a

    def get_connection_file_path(self, config_entry):
        connection_file_path = config_entry['connectionFilePath']
        if not os.path.isabs(config_entry['connectionFilePath']):
            connection_file_path = os.path.join(os.getcwd(), config_entry['connectionFilePath'])
        return connection_file_path

    def check_required_keys(self):
        for key in self.required_keys:
            test = self.config[key]