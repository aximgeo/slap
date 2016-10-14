import os

from .api import Api
from .config import ConfigParser
import arcpy


class Publisher:

    config_parser = ConfigParser()

    def __init__(self):

        arcpy.env.overwriteOutput = True
        
        connection_file_name = 'temp.ags'
        self.output_path = self.config_parser.get_full_path('./')
        self.connection_file_path = os.path.join(self.output_path, connection_file_name)

        self.config = None
        self.api = None

    def load_config(self, path_to_config):
        self.config = self.config_parser.load_config(path_to_config)

    def create_server_connection_file(self, username, password):
        connection_file_name = 'temp.ags'
        output_path = self.config_parser.get_full_path('./')
        self.connection_file_path = os.path.join(output_path, connection_file_name)
        arcpy.mapping.CreateGISServerConnectionFile(
            connection_type='PUBLISH_GIS_SERVICES',
            out_folder_path=self.output_path,
            out_name=connection_file_name,
            server_url=self.config['agsUrl'],
            server_type='ARCGIS_SERVER',
            use_arcgis_desktop_staging_folder=False,
            staging_folder_path=self.output_path,
            username=username,
            password=password,
            save_username_password=True
        )

    def init_api(self, ags_url, token_url, portal_url, certs, username, password):
        self.api = Api(
            ags_url=ags_url,
            token_url=token_url,
            portal_url=portal_url,
            certs=certs,
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
            service_name=config_entry["serviceName"] if "serviceName" in config_entry else filename,
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
            service_name=config_entry["serviceName"] if "serviceName" in config_entry else filename,
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
            service_name=config_entry["serviceName"] if "serviceName" in config_entry else filename,
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
        config_entry['json']['serviceName'] = config_entry["serviceName"] if "serviceName" in config_entry else filename

        output_directory = self.get_output_directory(config_entry)
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

    def publish_draft(self, sddraft, sd, config):
        self.stage_service_definition(sddraft, sd)
        self.delete_service(config)
        self.upload_service_definition(sd, config)
        self.update_service(config)

    def stage_service_definition(self, sddraft, sd):
        self.message("Staging service definition...")
        arcpy.StageService_server(sddraft, sd)

    def upload_service_definition(self, sd, config):
        self.message("Uploading service definition...")
        arcpy.UploadServiceDefinition_server(
            in_sd_file=sd,
            in_server=self.connection_file_path,
            in_startupType=config["initialState"] if "initialState" in config else "STARTED"
        )

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

    def message(self, message):
        print message


def only_one(iterable):
    it = iter(iterable)
    return any(it) and not any(it)
