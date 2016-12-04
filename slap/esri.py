import arcpy
import os


class ArcpyHelper:

    def __init__(self, username, password, ags_admin_url, connection_file_name='temp.ags'):

        arcpy.env.overwriteOutput = True

        # ESRI's tools will change the cwd, so set it at the beginning
        self._cwd = os.getcwd()

        self.connection_file_path = self.create_server_connection_file(
            username,
            password,
            ags_admin_url,
            connection_file_name
        )


    @property
    def cwd(self):
        return self._cwd

    def get_full_path(self, config_path):
        return os.path.normpath(config_path) if os.path.isabs(config_path) \
            else os.path.normpath(os.path.join(self.cwd, config_path))

    def get_output_directory(self, output_directory):
        return self.get_full_path(config_entry["output"]) if "output" in config_entry else self.get_full_path('output')

    @staticmethod
    def stage_service_definition(sddraft, sd):
        arcpy.StageService_server(sddraft, sd)

    def register_data_sources(self, data_sources):
        existing_data_sources = arcpy.ListDataStoreItems(self.connection_file_path, "FOLDER") + \
                                arcpy.ListDataStoreItems(self.connection_file_path, "DATABASE")
        for data_source in data_sources:
            if data_source["name"] not in existing_data_sources:
                self.register_data_source(data_source)

    def register_data_source(self, data_source):
        server_path = data_source["serverPath"]
        client_path = data_source["clientPath"] if "clientPath" in data_source else server_path
        name = data_source["name"]
        arcpy.AddDataStoreItem(
            connection_file=self.connection_file_path,
            datastore_type='DATABASE' if server_path.endswith('.sde') else 'FOLDER',
            connection_name=name,
            server_path=self.get_full_path(server_path),
            client_path=self.get_full_path(client_path)
        )

    def upload_service_definition(self, sd, initial_state="STARTED"):
        arcpy.UploadServiceDefinition_server(
            in_sd_file=sd,
            in_server=self.connection_file_path,
            in_startupType=initial_state
        )

    def create_server_connection_file(self, username, password, ags_admin_url, connection_file_name='temp.ags'):
        output_path = self.get_full_path('./')
        arcpy.mapping.CreateGISServerConnectionFile(
            connection_type='PUBLISH_GIS_SERVICES',
            out_folder_path=output_path,
            out_name=connection_file_name,
            server_url=ags_admin_url,
            server_type='ARCGIS_SERVER',
            use_arcgis_desktop_staging_folder=False,
            staging_folder_path=output_path,
            username=username,
            password=password,
            save_username_password=True
        )
        return os.path.join(output_path, connection_file_name)

    def set_workspaces(self, path_to_mxd, workspaces):
        full_mxd_path = self.get_full_path(path_to_mxd)
        mxd = arcpy.mapping.MapDocument(full_mxd_path)
        for workspace in workspaces:
            print("Replacing workspace " + workspace["old"]["path"] + " => " + workspace["new"]["path"])
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

    def publish_gp(self, config_entry, filename, sddraft):
        if "result" in config_entry:
            result = self.get_full_path(config_entry["result"])
        else:
            raise Exception("Result must be included in config for publishing a GP tool")

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

        mxd = arcpy.mapping.MapDocument(self.get_full_path(config_entry["input"]))
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