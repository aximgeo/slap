import os
import json

class ConfigParser:

    config = None

    def __init__(self):
        pass

    def load_config(self, path_to_config):
        with open(path_to_config) as config_file:
            self.config = json.load(config_file)
        return self.config

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