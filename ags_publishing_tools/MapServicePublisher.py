import os
import sys
import argparse
import json
from ags_publishing_tools.SdDraftParser import SdDraftParser
import arcpy

arcpy.env.overwriteOutput = True


class MapServicePublisher:

    config = None
    currentDirectory = str(os.path.dirname(os.path.abspath(__file__)) + os.path.sep).replace("\\", "/")
    draft_parser = SdDraftParser()

    def __init__(self):
        pass

    def load_config(self, path_to_config):
        with open(path_to_config) as config_file:
            self.config = json.load(config_file)

    def publish_gp(self, config_entry, connection_file_path):
        filename = os.path.splitext(os.path.split(self.currentDirectory + config_entry["input"])[1])[0]
        sddraft, sd = self.get_filenames(filename, self.get_output_directory(config_entry))

        if "result" in config_entry:
            result = os.path.join(self.currentDirectory, config_entry["result"])
        else:
            raise Exception("Result must be included in config for publishing a GP tool")

        self.message("Generating service definition draft for gp tool...")
        arcpy.CreateGPSDDraft(
            result=result,
            out_sddraft=sddraft,
            service_name=config_entry["serviceName"] if "serviceName" in config_entry else os.path.splitext(filename)[0],
            server_type=config_entry["serverType"] if "serverType" in config_entry else 'ARCGIS_SERVER',
            connection_file_path=connection_file_path,
            copy_data_to_server=config_entry["copyDataToServer"] if "copyDataToServer" in config_entry else False,
            folder_name=config_entry["folderName"] if "folderName" in config_entry else '',
            summary=config_entry["summary"] if "summary" in config_entry else '',
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

        analysis = arcpy.mapping.AnalyzeForSD(sddraft)

        if self.analysis_successful(analysis['errors']):
            self.publish_service(sddraft, sd, connection_file_path)

    def publish_mxd(self, config_entry, connection_file_path):
        filename = os.path.splitext(os.path.split(config_entry["input"])[1])[0]
        sddraft, sd = self.get_filenames(filename, self.get_output_directory(config_entry))
        mxd = arcpy.mapping.MapDocument(os.path.join(self.currentDirectory, config_entry["input"]))

        if "workspaces" in config_entry:
            self.set_workspaces(mxd, config_entry["workspaces"])

        self.message("Generating service definition draft for mxd...")
        arcpy.mapping.CreateMapSDDraft(
            map_document=mxd,
            out_sddraft=sddraft,
            service_name=config_entry["serviceName"] if "serviceName" in config_entry else filename,
            server_type=config_entry["serverType"] if "serverType" in config_entry else 'ARCGIS_SERVER',
            connection_file_path=connection_file_path,
            copy_data_to_server=config_entry["copyDataToServer"] if "copyDataToServer" in config_entry else False,
            folder_name=config_entry["folderName"] if "folderName" in config_entry else None,
            summary=config_entry["summary"] if "summary" in config_entry else None,
            tags=config_entry["tags"] if "tags" in config_entry else None
        )

        analysis = arcpy.mapping.AnalyzeForSD(sddraft)

        if self.analysis_successful(analysis['errors']):
            self.publish_service(sddraft, sd, connection_file_path)

    def publish_image_service(self, config_entry, connection_file_path):
        filename = os.path.splitext(os.path.split(config_entry["input"])[1])[0]
        sddraft, sd = self.get_filenames(filename, self.get_output_directory(config_entry))

        self.message("Generating service definition draft for image service...")
        arcpy.CreateImageSDDraft(
            raster_or_mosaic_layer=config_entry["input"],
            out_sddraft=sddraft,
            service_name=config_entry["serviceName"] if "serviceName" in config_entry else os.path.splitext(filename)[0],
            connection_file_path=connection_file_path,
            server_type=config_entry["serverType"] if "serverType" in config_entry else 'ARCGIS_SERVER',
            copy_data_to_server=config_entry["copyDataToServer"] if "copyDataToServer" in config_entry else False,
            folder_name=config_entry["folderName"] if "folderName" in config_entry else '',
            summary=config_entry["summary"] if "summary" in config_entry else '',
            tags=''
        )

        analysis = arcpy.mapping.AnalyzeForSD(sddraft)

        if self.analysis_successful(analysis['errors']):
            self.publish_service(sddraft, sd, connection_file_path)

    def get_output_directory(self, config_entry):
        return os.path.join(self.currentDirectory, (config_entry["output"] if "output" in config_entry else 'output/'))

    def set_workspaces(self, mxd, workspaces):
        mxd.relativePaths = True
        for workspace in workspaces:
            mxd.findAndReplaceWorkspacePaths(workspace["old"], workspace["new"], False)
        mxd.save()

    def analysis_successful(self, analysis_errors):
        if analysis_errors == {}:
            return True
        else:
            raise RuntimeError('Analysis contained errors: ', analysis_errors)

    def get_filenames(self, original_name, output_path):
        sddraft = os.path.join(output_path, '{}.' + 'sddraft').format(original_name)
        sd = os.path.join(output_path, '{}.' + 'sd').format(original_name)
        return sddraft, sd

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
            connection_file_path = os.path.join(self.currentDirectory, connection_file_path)
        return connection_file_path

    def publish_input(self, input_value):
        input_was_published = self.check_service_type('mapServices', input_value, self.publish_mxd)
        if not input_was_published:
            input_was_published = self.check_service_type('gpServices', input_value, self.publish_gp)
        if not input_was_published:
            input_was_published = self.check_service_type('imageServices', input_value, self.publish_image_service)
        if not input_was_published:
            raise ValueError('Input ' + input_value + ' was not found in config.')

    def check_service_type(self, type, value, method):
        ret = False
        if type in self.config:
            for config in self.config[type]['services']:
                if config["input"] == value:
                    self._publish_service('mapServices', method, config)
                    ret = True
                    break
        return ret

    def publish_service(self, sddraft, sd, server):
        self.message("Setting service configuration...")
        self.set_draft_configuration(sddraft)
        self.message("Staging service definition...")
        arcpy.StageService_server(sddraft, sd)
        self.message("Uploading service definition...")
        arcpy.UploadServiceDefinition_server(sd, server)

    def set_draft_configuration(self, sddraft):
        self.draft_parser.parse_sd_draft(sddraft)
        self.draft_parser.set_as_replacement_service()
        self.draft_parser.disable_schema_locking()
        self.draft_parser.save_sd_draft()

    def publish_all(self):
        self._publish_services('mapServices', self.publish_mxd)
        self._publish_services('imageServices', self.publish_image_service)
        self._publish_services('gpServices', self.publish_gp)

    def _publish_services(self, type_key, method):
        for config_entry in self.config[type_key]['services']:
            self._publish_service(type_key, method, config_entry)

    def _publish_service(self, type_key, method, config_entry):
        self.message("Publishing " + config_entry["input"])
        method(config_entry, self.get_connection_file_path(type_key, config_entry))
        self.message(config_entry["input"] + " published successfully")

    def message(self, message):
        print message

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config",
                        help="full path to config file (ex: --config c:/configs/int_config.json)")
    parser.add_argument("-i", "--inputs", action="append",
                        help="one or more inputs to publish (ex: -i mxd/bar -i gp/PrintService.tbx, -i \\\\my\\network\\share)")
    args = parser.parse_args()

    if not args.config:
        parser.error("Full path to config file is required")

    publisher = MapServicePublisher()
    print "Loading config..."
    publisher.load_config(args.config)
    if args.inputs:
        for i in args.inputs:
            publisher.publish_input(i)
    else:
        publisher.publish_all()

if __name__ == "__main__":
    main(sys.argv[1:])