from future import standard_library
standard_library.install_aliases()
from past.builtins import basestring
from builtins import str
from builtins import object
import os
import json
import urllib.parse
import re
from functools import reduce


class ConfigParser(object):

    service_types = ['mapServices', 'gpServices', 'imageServices']
    required_keys = ['input', 'agsUrl']

    def __init__(self):
        pass

    def load_config(self, path_to_config):
        return self.parse_config(self._load_config_from_file(path_to_config))

    @staticmethod
    def _load_config_from_file(path_to_config):
        with open(path_to_config) as config_file:
            return json.load(config_file)

    @staticmethod
    def _get_full_config_path(path_to_config):
        return path_to_config if os.path.isabs(path_to_config) else os.path.join(os.getcwd(), path_to_config)

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

    @staticmethod
    def get_type_keys(config, service_type):
        type_keys = {}
        for key in config:
            if key == service_type:
                for type_key in config[key]:
                    if type_key not in ['services']:
                        type_keys[type_key] = config[key][type_key]
        return type_keys

    def merge(self, a, b, path=None):
        if path is None:
            path = []
        for key in b:
            if key in a:
                if isinstance(a[key], dict) and isinstance(b[key], dict):
                    self.merge(a[key], b[key], path + [str(key)])
                elif a[key] == b[key]:
                    pass  # same leaf value
                else:
                    a[key] = b[key]  # Always overwrite
            else:
                a[key] = b[key]
        return a

    def merge_json(self, default_json, config_json):
        if isinstance(default_json, basestring):
            default_json_copy = json.loads(default_json)
        else:
            default_json_copy = default_json.copy()
        return self.merge(default_json_copy, config_json)

    @staticmethod
    def update_hostname(url, hostname):
        url_parts = urllib.parse.urlsplit(url)
        url_parts = url_parts._replace(netloc=re.sub('^[^:]*', hostname, url_parts.netloc))
        return urllib.parse.urlunsplit(url_parts)

    def check_required_keys(self, config):
        for key in self.required_keys:
            test = config[key]
