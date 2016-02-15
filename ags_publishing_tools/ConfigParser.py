import os
import json

class ConfigParser:

    config = None
    types = ['mapServices', 'gpServices', 'imageServices']

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


    def get_connection_file_path(self, type_key, config_entry):
        connection_key = "connectionFilePath"
        if connection_key in config_entry:
            connection_file_path = config_entry["connectionFilePath"]
        elif connection_key in self.config[type_key]:
            connection_file_path = self.config[type_key]["connectionFilePath"]
        elif connection_key in self.config:
            connection_file_path = self.config["connectionFilePath"]
        else:
            raise ValueError('connectionFilePath not specified for ' + config_entry)
        if not os.path.isabs(connection_file_path):
            connection_file_path = os.path.join(os.getcwd(), connection_file_path)
        return connection_file_path