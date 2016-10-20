import os
import argparse
from slap.api import Api
from slap.config import ConfigParser
from slap.arcpy_helper import ArcpyHelper
from slap import git


class Publisher:

    config = None
    arcpy_helper = None
    config_parser = ConfigParser()
    api = None

    def __init__(self):
        pass

    def load_config(self, path_to_config):
        self.config = self.config_parser.load_config(path_to_config)

    def init_arcpy_helper(self, username, password, ags_admin_url, filename):
        self.arcpy_helper = ArcpyHelper(username, password, ags_admin_url, filename)

    def init_api(self, ags_url, token_url, portal_url, certs, username, password):
        self.api = Api(
            ags_url=ags_url,
            token_url=token_url,
            portal_url=portal_url,
            certs=certs,
            username=username,
            password=password
        )

    @staticmethod
    def analysis_successful(analysis_errors):
        if analysis_errors == {}:
            return True
        else:
            raise RuntimeError('Analysis contained errors: ', analysis_errors)

    def get_sddraft_output(self, original_name, output_path):
        return self._get_output_filename(original_name, output_path, 'sddraft')

    def get_sd_output(self, original_name, output_path):
        return self._get_output_filename(original_name, output_path, 'sd')

    @staticmethod
    def _get_output_filename(original_name, output_path, extension):
        return os.path.join(output_path, '{}.' + extension).format(original_name)

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
        for type in self.config_parser.service_types:
            self.publish_services(type)

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
        config_entry['json']['serviceName'] = self._get_service_name_from_config(config_entry)

        output_directory = self.arcpy_helper.get_output_directory(config_entry)
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        sddraft = self.get_sddraft_output(filename, output_directory)
        sd = self.get_sd_output(filename, output_directory)
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


def only_one(iterable):
    it = iter(iterable)
    return any(it) and not any(it)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--username",
                        required=True,
                        help="Portal or AGS username (ex: --username john)")
    parser.add_argument("-p", "--password",
                        required=True,
                        help="Portal or AGS password (ex: --password myPassword)")
    parser.add_argument("-c", "--config",
                        required=True,
                        help="full path to config file (ex: --config c:/configs/int_config.json)")
    parser.add_argument("-i", "--inputs",
                        action="append",
                        help="one or more inputs to publish (ex: -i mxd/bar.mxd -i mxd/foo.mxd")
    parser.add_argument("-a", "--all",
                        action="store_true",
                        help="publish all entries in config")
    parser.add_argument("-g", "--git",
                        help="publish all mxd files that have changed between HEAD and this commit (ex: -g b45e095834af1bc8f4c348bb4aad66bddcadeab4")
    args = parser.parse_args()

    if not args.username:
        parser.error("username is required")

    if not args.password:
        parser.error("password is required")

    if not args.config:
        parser.error("Full path to config file is required")

    if not only_one([args.git, args.inputs, args.all]):
        parser.error("Specify only one of --git, --all, or --inputs")

    if not args.all and not args.inputs and not args.git:
        parser.error("Specify one of --git, --all, or --inputs")

    return args


def main():
    args = get_args()
    publisher = Publisher()
    print "Loading config..."
    publisher.load_config(args.config)
    publisher.init_arcpy_helper(args.username, args.password, publisher.config['agsUrl'])
    publisher.init_api(
        ags_url=publisher.config['agsUrl'],
        token_url=publisher.config['tokenUrl'] if 'tokenUrl' in publisher.config else None,
        portal_url=publisher.config['portalUrl'] if 'portalUrl' in publisher.config else None,
        certs=publisher.config['certs'] if 'certs' in publisher.config else True,
        username=args.username,
        password=args.password
    )
    if args.inputs:
        for i in args.inputs:
            publisher.publish_input(i)
    elif args.git:
        print "Getting changes from git..."
        changed_files = git.get_changed_mxds(args.git)
        print changed_files
        for i in changed_files:
            publisher.publish_input(i)
    elif args.all:
        publisher.publish_all()

if __name__ == "__main__":
    main()
