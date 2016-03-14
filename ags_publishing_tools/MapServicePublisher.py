import os
import argparse
from ags_publishing_tools.api import Api
from ags_publishing_tools.config import ConfigParser
from ags_publishing_tools import git
import arcpy

arcpy.env.overwriteOutput = True


class MapServicePublisher:

    config = None
    connection_file_path = None
    config_parser = ConfigParser()
    api = None

    def __init__(self):
        pass

    def load_config(self, path_to_config):
        self.config = self.config_parser.load_config(path_to_config)

    def create_server_connection_file(self, username, password):
        connection_file_name = 'temp.ags'
        output_path = self.config_parser.get_full_path('./')
        self.connection_file_path = os.path.join(output_path, connection_file_name)
        arcpy.mapping.CreateGISServerConnectionFile(
            connection_type='PUBLISH_GIS_SERVICES',
            out_folder_path=output_path,
            out_name=connection_file_name,
            server_url=self.config['agsUrl'],
            server_type='ARCGIS_SERVER',
            use_arcgis_desktop_staging_folder=False,
            staging_folder_path=output_path,
            username=username,
            password=password,
            save_username_password=True
        )

    def init_api(self, ags_url, token_url, portal_url, username, password):
        self.api = Api(
            ags_url=ags_url,
            token_url=token_url,
            portal_url=portal_url,
            username=username,
            password=password
        )

    def publish_gp(self, config_entry, filename, sddraft):
        if "result" in config_entry:
            result = self.config_parser.get_full_path(config_entry["result"])
        else:
            raise Exception("Result must be included in config for publishing a GP tool")

        self.message("Generating service definition draft for gp tool...")
        arcpy.CreateGPSDDraft(
            result=result,
            out_sddraft=sddraft,
            service_name=filename,
            server_type=config_entry["serverType"] if "serverType" in config_entry else 'ARCGIS_SERVER',
            connection_file_path=self.connection_file_path,
            copy_data_to_server=config_entry["copyDataToServer"] if "copyDataToServer" in config_entry else False,
            folder_name=config_entry["folderName"] if "folderName" in config_entry else None,
            summary=config_entry["summary"] if "summary" in config_entry else None,
            tags=config_entry["tags"] if "tags" in config_entry else None,
            executionType=config_entry["executionType"] if "executionType" in config_entry else 'Asynchronous',
            resultMapServer=False,
            showMessages="INFO",
            maximumRecords=5000,
            minInstances=2,
            maxInstances=3,
            maxUsageTime=100,
            maxWaitTime=10,
            maxIdleTime=180
        )
        return arcpy.mapping.AnalyzeForSD(sddraft)

    def publish_mxd(self, config_entry, filename, sddraft):
        if "workspaces" in config_entry:
            self.set_workspaces(config_entry["input"], config_entry["workspaces"])

        mxd = arcpy.mapping.MapDocument(self.config_parser.get_full_path(config_entry["input"]))

        self.message("Generating service definition draft for mxd...")
        arcpy.mapping.CreateMapSDDraft(
            map_document=mxd,
            out_sddraft=sddraft,
            service_name=filename,
            server_type=config_entry["serverType"] if "serverType" in config_entry else 'ARCGIS_SERVER',
            connection_file_path=self.connection_file_path,
            copy_data_to_server=config_entry["copyDataToServer"] if "copyDataToServer" in config_entry else False,
            folder_name=config_entry["folderName"] if "folderName" in config_entry else None,
            summary=config_entry["summary"] if "summary" in config_entry else None,
            tags=config_entry["tags"] if "tags" in config_entry else None
        )
        return arcpy.mapping.AnalyzeForSD(sddraft)

    def publish_image_service(self, config_entry, filename, sddraft):
        self.message("Generating service definition draft for image service...")
        arcpy.CreateImageSDDraft(
            raster_or_mosaic_layer=config_entry["input"],
            out_sddraft=sddraft,
            service_name=filename,
            connection_file_path=self.connection_file_path,
            server_type=config_entry["serverType"] if "serverType" in config_entry else 'ARCGIS_SERVER',
            copy_data_to_server=config_entry["copyDataToServer"] if "copyDataToServer" in config_entry else False,
            folder_name=config_entry["folderName"] if "folderName" in config_entry else None,
            summary=config_entry["summary"] if "summary" in config_entry else None,
            tags=config_entry["tags"] if "tags" in config_entry else None
        )
        return arcpy.mapping.AnalyzeForSD(sddraft)

    def get_output_directory(self, config_entry):
        return self.config_parser.get_full_path(config_entry["output"]) if "output" in config_entry else self.config_parser.get_full_path('output')

    def set_workspaces(self, path_to_mxd, workspaces):
        full_mxd_path = self.config_parser.get_full_path(path_to_mxd)
        mxd = arcpy.mapping.MapDocument(full_mxd_path)
        for workspace in workspaces:
            self.message("Replacing workspace " + workspace["old"]["path"] + " => " + workspace["new"]["path"])
            mxd.replaceWorkspaces(
                old_workspace_path=workspace["old"]["path"],
                old_workspace_type=workspace["old"]["type"] if "type" in workspace["old"] else "SDE_WORKSPACE",
                new_workspace_path=workspace["new"]["path"],
                new_workspace_type=workspace["new"]["type"] if "type" in workspace["new"] else "SDE_WORKSPACE",
                validate=False
            )
        mxd.relativePaths = True
        mxd.save()
        del mxd

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
            return self.publish_mxd
        if type == 'imageServices':
            return self.publish_image_service
        if type == 'gpServices':
            return self.publish_gp
        raise ValueError('Invalid type: ' + type)

    def publish_services(self, type):
        for config_entry in self.config[type]['services']:
            self.publish_service(type, config_entry)

    def publish_service(self, service_type, config_entry):
        filename = os.path.splitext(os.path.split(config_entry["input"])[1])[0]
        config_entry['json']['serviceName'] = filename
        sddraft = self.get_sddraft_output(filename, self.get_output_directory(config_entry))
        sd = self.get_sd_output(filename, self.get_output_directory(config_entry))
        self.message("Publishing " + config_entry["input"])
        analysis = self._get_method_by_type(service_type)(config_entry, filename, sddraft)
        if self.analysis_successful(analysis['errors']):
            self.publish_draft(sddraft, sd, config_entry)
            self.message(config_entry["input"] + " published successfully")
        else:
            self.message("Error publishing " + config_entry['input'] + analysis)

    def publish_draft(self, sddraft, sd, config):
        self.message("Staging service definition...")
        arcpy.StageService_server(sddraft, sd)
        self.message("Deleting old service...")
        self.api.delete_service(config['json']['serviceName'],
                                config["folderName"] if "folderName" in config else None)
        self.message("Uploading service definition...")
        arcpy.UploadServiceDefinition_server(sd, self.connection_file_path)
        self.update_service(config)

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

    def message(self, message):
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
                        action="store_true",
                        help="publish all mxd files that have changed since the last commit")
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
    publisher = MapServicePublisher()
    print "Loading config..."
    publisher.load_config(args.config)
    publisher.create_server_connection_file(args.username, args.password)
    publisher.init_api(
        ags_url=publisher.config['agsUrl'],
        token_url=publisher.config['tokenUrl'],
        portal_url=publisher.config['portalUrl'] if 'portalUrl' in publisher.config else None,
        username=args.username,
        password=args.password
    )
    if args.inputs:
        for i in args.inputs:
            publisher.publish_input(i)
    elif args.git:
        print "Getting changes from git..."
        changed_files = git.get_changed_mxds()
        print changed_files
        for i in changed_files:
            publisher.publish_input(i)
    elif args.all:
        publisher.publish_all()

if __name__ == "__main__":
    main()
