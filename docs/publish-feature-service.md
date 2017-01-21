# Enabling feature access in a map service

To enable feature access on a map service, you must enable the `FeatureServer` 
extension in the service `json` parameter - the easiet way to get the 
`FeatureSerer` JSON is to go the REST Admin endpoint for a service with 
feature access enabled, copy it, and modify it for your needs.


```javascript
{
    "input": "D:\\path-to\\my.mxd",
    "output": "output/",
    "serviceName": "My Service",
    "initialState": "STOPPED",
    "serverType": "ARCGIS_SERVER",
    "copyDataToServer": "False",
    "folderName": "Hydrants",
    "summary": "",
    "workspaces": [{
        "old": {
            "path": "\\\\old-path\conn.sde",
            "type": "SDE_WORKSPACE"
        },
        "new": {
            "path": "D:\\new-path\conn.sde",
            "type": "SDE_WORKSPACE"
        }
    }],
    "json": {
        "extensions": [{
            "typeName": "FeatureServer",
            "capabilities": "Create,Delete,Query,Update,Uploads,Editing",
            "enabled": "true",
            "maxUploadFileSize": 0,
            "allowedUploadFileTypes": "",
            "properties": {
                "creatorPresent": "true",
                "dataInGdb": "true",
                "xssPreventionEnabled": "true",
                "allowGeometryUpdates": "true",
                "versionedData": "true",
                "syncVersionCreationRule": "versionPerDownloadedMap",
                "maxRecordCount": "1000",
                "allowOthersToQuery": "true",
                "syncEnabled": "false",
                "editorTrackingTimeZoneID": "UTC",
                "enableZDefaults": "false",
                "realm": "",
                "allowOthersToDelete": "false",
                "allowTrueCurvesUpdates": "false",
                "datasetInspected": "true",
                "editorTrackingRespectsDayLightSavingTime": "false",
                "zDefaultValue": "0",
                "enableOwnershipBasedAccessControl": "false",
                "editorTrackingTimeInUTC": "true",
                "allowOthersToUpdate": "false"
            }
        }]
    }
}
````