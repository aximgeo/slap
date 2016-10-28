import os
from slap.api import Api
from slap.config import ConfigParser
from slap.esri import ArcpyHelper


class Publisher:

    def __init__(self, username, password, config):
        self.config_parser = ConfigParser()
        self.config = self.config_parser.load_config(config) if isinstance(config, basestring) else config
        self.arcpy_helper = ArcpyHelper(
            username=username,
            password=password,
            ags_admin_url=self.config['agsUrl']
        )
        self.api = Api(
            ags_url=self.config['agsUrl'],
            token_url=self.config['tokenUrl'] if 'tokenUrl' in self.config else None,
            portal_url=self.config['portalUrl'] if 'portalUrl' in self.config else None,
            username=username,
            password=password
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
                input_was_published = self.check_service_type(service_type, input_value)
        if not input_was_published:
            raise ValueError('Input ' + input_value + ' was not found in config.')

    def check_service_type(self, service_type, value):
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

    def _get_method_by_type(self, type):
        if type == 'mapServices':
            return self.arcpy_helper.publish_mxd
        if type == 'imageServices':
            return self.arcpy_helper.publish_image_service
        if type == 'gpServices':
            return self.arcpy_helper.publish_gp
        raise ValueError('Invalid type: ' + type)

    def publish_services(self, type):
        for config_entry in self.config[type]['services']:
            self.publish_service(type, config_entry)

    def publish_service(self, service_type, config_entry):
        filename = os.path.splitext(os.path.split(config_entry["input"])[1])[0]
        if 'json' not in config_entry:
            config_entry['json'] = {}
        config_entry['json']['serviceName'] = self._get_service_name_from_config(config_entry)

        output_directory = self.arcpy_helper.get_output_directory(config_entry)
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        sddraft = os.path.join(output_directory, '{}.' + "sddraft").format(filename)
        sd = os.path.join(output_directory, '{}.' + "sd").format(filename)
        self.message("Publishing " + config_entry["input"])
        analysis = self._get_method_by_type(service_type)(config_entry, filename, sddraft)
        if self.analysis_successful(analysis['errors']):
            self.publish_draft(sddraft, sd, config_entry)
            self.message(config_entry["input"] + " published successfully")
        else:
            self.message("Error publishing " + config_entry['input'] + analysis)

    @staticmethod
    def _get_service_name_from_config(config_entry):
        if "serviceName" in config_entry:
            return config_entry['serviceName']
        elif 'json' in config_entry and 'serviceName' in config_entry['json']:
            return config_entry['json']['serviceName']
        else:
            return os.path.splitext(os.path.split(config_entry["input"])[1])[0]

    def publish_draft(self, sddraft, sd, config):
        self.arcpy_helper.stage_service_definition(sddraft, sd)
        self.delete_service(config)
        self.arcpy_helper.upload_service_definition(sd, config)
        self.update_service(config)

    def delete_service(self, config):
        service_exists = self.api.service_exists(
            config['json']['serviceName'],
            config["folderName"] if "folderName" in config else None
        )
        if service_exists['exists']:
            self.message("Deleting old service...")
            self.api.delete_service(
                config['json']['serviceName'],
                config["folderName"] if "folderName" in config else None
            )

    def update_service(self, config):
        if 'json' in config:
            default_json = self.api.get_service_params(
                service_name=config['json']['serviceName'],
                folder=config["folderName"] if "folderName" in config else None
            )
            json = self.config_parser.merge_json(default_json, config['json'])
            self.api.edit_service(
                service_name=config['json']['serviceName'],
                folder=config["folderName"] if "folderName" in config else None,
                params=json
            )

    @staticmethod
    def message(message):
        print message



