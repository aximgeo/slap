import os
import sys
import getopt
import imp
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

        arcpy.CreateGPSDDraft(result=result,
                              out_sddraft=sddraft,
                              service_name=config_entry["serviceName"],
                              server_type=config_entry["serverType"],
                              connection_file_path=self.currentDirectory + config_entry["connectionFilePath"],
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
        self.set_data_sources(mxd, self.currentDirectory + config_entry["dbConnectionFilePath"])

        analysis = arcpy.mapping.CreateMapSDDraft(map_document=mxd,
                                                  out_sddraft=sddraft,
                                                  service_name=config_entry["serviceName"],
                                                  server_type=config_entry["serverType"],
                                                  connection_file_path=self.currentDirectory + config_entry["connectionFilePath"],
                                                  copy_data_to_server=config_entry["copyDataToServer"],
                                                  folder_name=config_entry["folderName"],
                                                  summary=config_entry["summary"]
                                                  )

        if self.analysis_successful(analysis['errors']):
            self.publish_service(sddraft, sd, self.currentDirectory + config_entry["connectionFilePath"])

    def set_data_sources(self, mxd, path_to_db_connection_file):
        mxd.replaceWorkspaces('', 'NONE', path_to_db_connection_file, 'SDE_WORKSPACE')

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
        arcpy.StageService_server(sddraft, sd)
        arcpy.UploadServiceDefinition_server(sd, server)

    def publish(self, services):
        for service_config in services:
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


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "h")
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    if len(args) == 1:
        publisher = MapServicePublisher()
        config = imp.load_source('config', args[0])
        publisher.publish(config.services)
    else:
        usage()
        sys.exit()


def usage():
    print ("python MapServicePublisher.py path_to_config")

if __name__ == "__main__":
    main(sys.argv[1:])