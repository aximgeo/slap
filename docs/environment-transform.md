# Deploying to a different environment

To publish the same set of services to a production environment, we'll create a new connection file, `prod.json`.  In our production environment, we want a few changes:

* A different set of connection files
* Schema locking to be *enabled*
* `maxIdleTime` to be 300ms, instead of the default 600

Our config file should look like:

``` json
{
    "agsUrl": "https://prodagsserver.com:6443/arcgis/admin",
    "mapServices": {
        "json": {
            "maxIdleTime": 300,
            "properties": {
                "schemaLockingEnabled": true
            }  
        },
        "services": [
            {
                "input": "Map1.mxd",
                "workspaces": [
                    {
                        "old": {"path": "c:/path/to/integration/connectionFile.sde"},
                        "new": {"path": "c:/path/to/production/connectionFile.sde"}
                    }
                ]
            },
            {
                "input": "Map2.mxd",
                "workspaces": [
                    {
                        "old": {"path": "c:/path/to/integration/connectionFile.sde"},
                        "new": {"path": "c:/path/to/production/connectionFile.sde"}
                    },
                    {
                        "old": {"path": "c:/path/to/integration/connectionFile2.sde"},
                        "new": {"path": "c:/path/to/production/connectionFile2.sde"}
                    }
                ]
            }
        ]
    }
}
```

To republish all the services using the production config file, we can do
```
slap --config prod.json --username <myProductionUsername> --password <myProductionPassword>
```
