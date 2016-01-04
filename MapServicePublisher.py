import os
import sys
import argparse
import imp
import xml.dom.minidom as DOM
import arcpy

arcpy.env.overwriteOutput = True


class MapServicePublisher:

    currentDirectory = os.path.dirname(os.path.abspath(__file__)) + '/'

    def __init__(self):
        pass

    def publish_gp(self, config_entry):
        filename = os.path.splitext(os.path.split(self.currentDirectory + config_entry["input"])[1])[0]
        sddraft, sd = self.get_filenames(filename, self.currentDirectory + config_entry["output"])
        result = self.get_result(self.currentDirectory + config_entry["input"], config_entry["toolbox"], config_entry["tool"])

        self.message("Generating service definition draft for gp tool...")
        arcpy.CreateGPSDDraft(result=result,
                              out_sddraft=sddraft,
                              service_name=config_entry["serviceName"],
                              server_type=config_entry["serverType"],
                              copy_data_to_server=config_entry["copyDataToServer"],
                              folder_name=config_entry["folderName"],
                              summary=config_entry["summary"],
                              tags="gp",
                              executionType=config_entry["executionType"],
                              resultMapServer=False,
                              showMessages="INFO",
                              maximumRecords=5000,
                              minInstances=2,
                              maxInstances=3,
                              maxUsageTime=100,
                              maxWaitTime=10,
                              maxIdleTime=180)

        analysis = arcpy.mapping.AnalyzeForSD(sddraft)

        if self.analysis_successful(analysis['errors']):
            self.publish_service(sddraft, sd, self.currentDirectory + config_entry["connectionFilePath"])

    def get_result(self, path_to_toolbox, toolbox, tool):
        arcpy.ImportToolbox(path_to_toolbox, toolbox)
        exetoolexp = 'arcpy.' + tool + '_' + toolbox
        exetool = eval(exetoolexp)
        return exetool()

    def publish_mxd(self, config_entry):
        filename = os.path.splitext(os.path.split(self.currentDirectory + config_entry["input"])[1])[0]
        sddraft, sd = self.get_filenames(filename, self.currentDirectory + config_entry["output"])
        mxd = arcpy.mapping.MapDocument(self.currentDirectory + config_entry["input"])

        if config_entry["workspaces"]:
            self.set_workspaces(mxd, config_entry["workspaces"])

        self.message("Generating service definition draft for mxd...")
        arcpy.mapping.CreateMapSDDraft(map_document=mxd,
                                       out_sddraft=sddraft,
                                       service_name=config_entry["serviceName"],
                                       server_type=config_entry["serverType"],
                                       copy_data_to_server=config_entry["copyDataToServer"],
                                       folder_name=config_entry["folderName"],
                                       summary=config_entry["summary"]
                                       )

        analysis = arcpy.mapping.AnalyzeForSD(sddraft)

        if self.analysis_successful(analysis['errors']):
            self.publish_service(sddraft, sd, self.currentDirectory + config_entry["connectionFilePath"])

    def set_as_replacement_service(self, sddraft):
        newType = 'esriServiceDefinitionType_Replacement'
        xml = sddraft
        doc = DOM.parse(xml)
        descriptions = doc.getElementsByTagName('Type')
        for desc in descriptions:
            if desc.parentNode.tagName == 'SVCManifest':
                if desc.hasChildNodes():
                    desc.firstChild.data = newType
        outXml = xml
        f = open(outXml, 'w')
        doc.writexml(f)
        f.close()

    def set_workspaces(self, mxd, workspaces):
        mxd.relativePaths = True
        for workspace in workspaces:
            mxd.findAndReplaceWorkspacePaths(workspace["old"], workspace["new"], True)
        mxd.save()

    def analysis_successful(self, analysis_errors):
        if analysis_errors == {}:
            return True
        else:
            raise RuntimeError('Analysis contained errors: ', analysis_errors)

    def get_filenames(self, original_name, output_path):
        sddraft = self.swap_extension(original_name, output_path, 'sddraft')
        sd = self.swap_extension(original_name, output_path, 'sd')
        return sddraft, sd

    def swap_extension(self, mxd_name, output_path, extension):
        new_name = os.path.join(output_path, '{}.' + extension).format(mxd_name)
        return new_name

    def publish_service(self, sddraft, sd, server):
        self.message("Setting draft as replacement...")
        self.set_as_replacement_service(sddraft)
        self.message("Staging service definition...")
        arcpy.StageService_server(sddraft, sd)
        self.message("Uploading service definition...")
        arcpy.UploadServiceDefinition_server(sd, server)

    def publish(self, services):
        for service_config in services:
            self.message("Publishing " + service_config["input"])
            extension = os.path.splitext(self.currentDirectory + service_config["input"])[1]
            self.get_publication_method_by_service_type(extension)(service_config)
            print service_config["input"] + " published successfully"

    def get_publication_method_by_service_type(self, extension):
        publication_methods = {
            '.mxd': self.publish_mxd,
            '.tbx': self.publish_gp
        }
        return publication_methods[extension.lower()]

    def slashes_to_dots(self, path):
        return path.replace('/', '.').replace('\\', '.')

    def message(self, message):
        print message


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="full path to config file (ex: -m c:/configs/int_config.json)")
    args = parser.parse_args()

    if not args.config:
        parser.error("Full path to config file is required")

    publisher = MapServicePublisher()
    config = imp.load_source('config', args.config)
    publisher.publish(config.services)

if __name__ == "__main__":
    main(sys.argv[1:])