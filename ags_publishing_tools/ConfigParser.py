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
            extra_keys = self.get_non_type_keys(config, type)
            copy = config[type].copy()
            for service in copy['services']:
                service.update(extra_keys)
        return copy

    def get_non_type_keys(self, config, type):
        new_keys = {}
        for key in config:
            if key not in self.types:
                new_keys[key] = config[key]
            if key == type:
                for type_key in config[key]:
                    if type_key not in ['services']:
                        new_keys[type_key] = config[key][type_key]
        return new_keys

    def get_connection_file_path(self, config_entry):
        connection_file_path = config_entry['connectionFilePath']
        if not os.path.isabs(config_entry['connectionFilePath']):
            connection_file_path = os.path.join(os.getcwd(), config_entry['connectionFilePath'])
        return connection_file_path

    def check_required_keys(self):
        for key in self.required_keys:
            test = self.config[key]