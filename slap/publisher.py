from __future__ import print_function
from past.builtins import basestring
from builtins import object
import os
from slap.api import Api
from slap.config import ConfigParser


class Publisher(object):

    def __init__(self, username, password, config, hostname=None):
        self.config_parser = ConfigParser()
        self.config = self.config_parser.load_config(config) if isinstance(config, basestring) else config

        # Allow the user to specify a host as an argument, in case it's set dynamically
        if hostname:
            self.config['agsUrl'] = self.config_parser.update_hostname(self.config['agsUrl'], hostname)

        self.api = Api(
            ags_url=self.config['agsUrl'],
            token_url=self.config['tokenUrl'] if 'tokenUrl' in self.config else None,
            portal_url=self.config['portalUrl'] if 'portalUrl' in self.config else None,
            username=username,
            password=password,
            verify_certs=self.config['verifyCerts'] if 'verifyCerts' in self.config else False
        )

        # This is a S-L-O-W import, so defer as long as possible
        from slap.esri import ArcpyHelper
        self.arcpy_helper = ArcpyHelper(
            username=username,
            password=password,
            ags_admin_url=self.config['agsUrl']
        )

    @staticmethod
    def analysis_successful(analysis_errors):
        if analysis_errors == {}:
            return True
        else:
            raise RuntimeError('Analysis contained errors: ', analysis_errors)

    def publish_input(self, input_value):
        input_was_published = False
        for service_type in self.config_parser.service_types:
            if not input_was_published:
                input_was_published = self._check_service_type(service_type, input_value)
        if not input_was_published:
            raise ValueError('Input ' + input_value + ' was not found in config.')

    def _check_service_type(self, service_type, value):
        ret = False
        if service_type in self.config:
            for config in self.config[service_type]['services']:
                if config["input"] == value:
                    self.publish_service(service_type, config)
                    ret = True
                    break
        return ret

    def publish_all(self):
        for service_type in self.config_parser.service_types:
            self.publish_services(service_type)

    def publish_services(self, service_type):
        for config_entry in self.config[service_type]['services']:
            self.publish_service(service_type, config_entry)

    def publish_service(self, service_type, config_entry):
        input_path, output_path, service_name, folder_name, json, initial_state = \
            self._get_publishing_params_from_config(config_entry)
        filename, sddraft, sd = self._get_service_definition_paths(input_path, output_path)

        self.message("Publishing " + input_path)
        analysis = self._get_method_by_service_type(service_type)(config_entry, filename, sddraft)
        if self.analysis_successful(analysis['errors']):  # This may throw an exception
            self.publish_sd_draft(sddraft, sd, service_name, folder_name, initial_state, json)
            self.message(input_path + " published successfully")

    def _get_publishing_params_from_config(self, config_entry):
        input_path = config_entry['input']
        output_path = config_entry['output'] if 'output' in config_entry else 'output'
        service_name = self._get_service_name_from_config(config_entry)
        folder_name = config_entry["folderName"] if "folderName" in config_entry else None
        json = config_entry['json'] if 'json' in config_entry else {}
        initial_state = config_entry["initialState"] if "initialState" in config_entry else "STARTED"
        return input_path, output_path, service_name, folder_name, json, initial_state

    @staticmethod
    def _get_service_name_from_config(config_entry):
        if "serviceName" in config_entry:
            return config_entry['serviceName']
        elif 'json' in config_entry and 'serviceName' in config_entry['json']:
            return config_entry['json']['serviceName']
        else:
            return os.path.splitext(os.path.split(config_entry["input"])[1])[0]

    def _get_service_definition_paths(self, input_path, output_path):
        filename = os.path.splitext(os.path.split(input_path)[1])[0]
        output_directory = self._create_output_directory(output_path)
        sddraft = os.path.join(output_directory, '{}.' + "sddraft").format(filename)
        sd = os.path.join(output_directory, '{}.' + "sd").format(filename)
        return filename, sddraft, sd

    def _create_output_directory(self, output_path):
        output_directory = self.arcpy_helper.get_full_path(output_path)
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        return output_directory

    def _get_method_by_service_type(self, service_type):
        if service_type == 'mapServices':
            return self.arcpy_helper.publish_mxd
        if service_type == 'imageServices':
            return self.arcpy_helper.publish_image_service
        if service_type == 'gpServices':
            return self.arcpy_helper.publish_gp
        raise ValueError('Invalid type: ' + service_type)

    def publish_sd_draft(self, path_to_sddraft, path_to_sd, service_name, folder_name=None, initial_state='STARTED', json=None):
        self.arcpy_helper.stage_service_definition(sddraft=path_to_sddraft, sd=path_to_sd)
        self.delete_service(service_name=service_name, folder_name=folder_name)
        self.arcpy_helper.upload_service_definition(sd=path_to_sd, initial_state=initial_state)
        if json:
            self.update_service(service_name=service_name, json=json, folder_name=folder_name)

    def delete_service(self, service_name, folder_name=None):
        service_exists = self.api.service_exists(service_name=service_name, folder=folder_name)
        if service_exists['exists']:
            self.message("Deleting old service...")
            self.api.delete_service(service_name=service_name, folder=folder_name)

    def update_service(self, service_name, folder_name=None, json=None):
        default_json = self.api.get_service_params(service_name=service_name, folder=folder_name)
        json = self.config_parser.merge_json(default_json, json if json else {})
        self.api.edit_service(service_name=service_name, folder=folder_name, params=json)

    def register_data_sources(self):
        if "dataSources" in self.config:
            self.arcpy_helper.register_data_sources(self.config["dataSources"])

    @staticmethod
    def message(message):
        print(message)



