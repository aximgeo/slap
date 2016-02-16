import os
import argparse
from ags_publishing_tools.SdDraftParser import SdDraftParser
from ags_publishing_tools.ConfigParser import ConfigParser
import arcpy

arcpy.env.overwriteOutput = True

class MapServicePublisher:

    config = None
    draft_parser = SdDraftParser()
    config_parser = ConfigParser()

    def __init__(self):
        pass

    def load_config(self, path_to_config):
        self.config = self.config_parser.load_config(path_to_config)

    def publish_gp(self, config_entry, filename, sddraft):

        if "result" in config_entry:
            if os.path.isabs(config_entry["result"]):
                result = config_entry["result"]
            else:
                result = self.config_parser.get_full_path(config_entry["result"])
        else:
            raise Exception("Result must be included in config for publishing a GP tool")

        self.message("Generating service definition draft for gp tool...")
        arcpy.CreateGPSDDraft(
            result=result,
            out_sddraft=sddraft,
            service_name=config_entry["serviceName"] if "serviceName" in config_entry else filename,
            server_type=config_entry["serverType"] if "serverType" in config_entry else 'ARCGIS_SERVER',
            connection_file_path=self.config_parser.get_full_path(config_entry["connectionFilePath"]),
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

        return arcpy.mapping.AnalyzeForSD(sddraft)

    def publish_mxd(self, config_entry, filename, sddraft):
        mxd = arcpy.mapping.MapDocument(self.config_parser.get_full_path(config_entry["input"]))

        if "workspaces" in config_entry:
            self.set_workspaces(mxd, config_entry["workspaces"])

        self.message("Generating service definition draft for mxd...")
        arcpy.mapping.CreateMapSDDraft(
            map_document=mxd,
            out_sddraft=sddraft,
            service_name=config_entry["serviceName"] if "serviceName" in config_entry else filename,
            server_type=config_entry["serverType"] if "serverType" in config_entry else 'ARCGIS_SERVER',
            connection_file_path=self.config_parser.get_full_path(config_entry["connectionFilePath"]),
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
            connection_file_path=self.config_parser.get_full_path(config_entry["connectionFilePath"]),
            server_type=config_entry["serverType"] if "serverType" in config_entry else 'ARCGIS_SERVER',
            copy_data_to_server=config_entry["copyDataToServer"] if "copyDataToServer" in config_entry else False,
            folder_name=config_entry["folderName"] if "folderName" in config_entry else '',
            summary=config_entry["summary"] if "summary" in config_entry else '',
            tags=''
        )

        return arcpy.mapping.AnalyzeForSD(sddraft)

    def get_output_directory(self, config_entry):
        return self.config_parser.get_full_path(config_entry["output"]) if "output" in config_entry else 'output/'

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

    def get_sddraft_output(self, original_name, output_path):
        return self._get_output_filename(original_name, output_path, 'sddraft')

    def get_sd_output(self, original_name, output_path):
        return self._get_output_filename(original_name, output_path, 'sd')

    def _get_output_filename(self, original_name, output_path, extension):
        return os.path.join(output_path, '{}.' + extension).format(original_name)

    def publish_input(self, input_value):
        input_was_published = self.check_service_type('mapServices', input_value)
        if not input_was_published:
            input_was_published = self.check_service_type('gpServices', input_value)
        if not input_was_published:
            input_was_published = self.check_service_type('imageServices', input_value)
        if not input_was_published:
            raise ValueError('Input ' + input_value + ' was not found in config.')

    def check_service_type(self, type, value):
        ret = False
        if type in self.config:
            for config in self.config[type]['services']:
                if config["input"] == value:
                    self.publish_service(type, config)
                    ret = True
                    break
        return ret

    def publish_all(self):
        for type in self.config_parser.types:
            self.publish_services(type)

    def _get_method_by_type(self, type):
        if type == 'mapServices': return self.publish_mxd
        if type == 'imageServices': return self.publish_image_service
        if type == 'gpServices': return self.publish_gp
        raise ValueError('Invalid type: ' + type)

    def publish_services(self, type):
        for config_entry in self.config[type]['services']:
            self.publish_service(type, config_entry)

    def publish_service(self, type, config_entry):
        filename = os.path.splitext(os.path.split(config_entry["input"])[1])[0]
        sddraft = self.get_sddraft_output(filename, self.get_output_directory(config_entry))
        self.message("Publishing " + config_entry["input"])
        analysis = self._get_method_by_type(type)(config_entry, filename, sddraft)
        if self.analysis_successful(analysis['errors']):
            self.publish_draft(sddraft, config_entry)
            self.message(config_entry["input"] + " published successfully")
        else:
            self.message("Error publishing " + config_entry['input'] + analysis)

    def publish_draft(self, sddraft, config):
        sd = self.swap_extension(sddraft, 'sd')
        self.message("Setting service configuration...")
        self.set_draft_configuration(sddraft, config["properties"] if "properties" in config else {})
        self.message("Staging service definition...")
        arcpy.StageService_server(sddraft, sd)
        self.message("Uploading service definition...")
        arcpy.UploadServiceDefinition_server(sd, config["connectionFilePath"])

    def swap_extension(self, input, extension):
        file, ext = os.path.splitext(input)
        return file + extension

    def set_draft_configuration(self, sddraft, properties):
        self.draft_parser.parse_sd_draft(sddraft)
        self.draft_parser.set_as_replacement_service()
        for key, value in properties:
            self.draft_parser.set_configuration_property(key, value)
        self.draft_parser.save_sd_draft()

    def message(self, message):
        print message


def main():
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
    main()
