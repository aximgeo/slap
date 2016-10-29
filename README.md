[![Build Status](https://travis-ci.org/gisinc/slap.svg?branch=master)](https://travis-ci.org/gisinc/slap)

# SLAP Maps: Simple Library for Automated Publishing of Map Services

Provides a way to automate the process of publishing map services; there are two main use cases:

1. Tracking MXDs via git, and using continuous integration to publish services
2. Promoting a set of map services through a series of environments (i.e., integration, acceptance, production) that require differing configuration per environment.

# Quick Setup
Install from pip using `pip install slap`

# Usage
```shell
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        Portal or AGS username (ex: --username john)
  -p PASSWORD, --password PASSWORD
                        Portal or AGS password (ex: --password myPassword)
  -c CONFIG, --config CONFIG
                        full path to config file (ex: --config
                        c:/configs/int_config.json)
  -s, --site            create a site before publishing
  -i INPUTS, --inputs INPUTS
                        one or more inputs to publish (ex: -i mxd/bar.mxd -i
                        mxd/foo.mxd
  -a, --all             publish all entries in config
  -g GIT, --git GIT     publish all mxd files that have changed between HEAD
                        and this commit (ex: -g
                        b45e095834af1bc8f4c348bb4aad66bddcadeab4
```

## Required Artifacts
There are a few artifacts that need to be generated (via ArcMap) per service and/or environment, which are required for the process to run.  These can be checked into source control if desired, and pulled down as needed.

- MXD files: "Source" document for map services
- Database connection files: Needed per environment for publishing map services
- Config files: Needed per environment to specify publishing parameters
- Username/password: Credentials for publishing.  These are *not* specified in the configuration file, but are passed in at the command line.

## Specifying inputs to publish
The script supports three main ways to specify MXD inputs: `--all`, `--git` and `--inputs`

### --all
Publish all MXDs specified in the config file, i.e.
```
slap --config int.json --username <myUsername> --password <myPassword> --all
```

### --git
Publish all MXDs that changed since the last git revision; this is mainly used from a CI server.
```
slap --config int.json --username <myUsername> --password <myPassword> --git
```

### --inputs
Publish one or more specific MXDs; note that `--inputs` can be specifed multiple times, i.e.
```
slap --config int.json --username <myUsername> --password <myPassword> --inputs map1.mxd, --inputs map2.mxd
```

## Config files
Configuration files are handled per-environment; for example, you might have three separate config files, `INT_config.json`, `UAT_config.json`, and `PROD_config.json`.
Each service is included in the config file as an object, grouped by service type.  *Note*:  Currently, only map services are supported.

An example configuration file might look like below.  *Note:* The comments would need to be removed, json is not valid with them.

``` javascript
{
    "agsUrl": "https://myagsserver.com:6443/arcgis/admin", // Required, URL for AGS admin endpoint
    "tokenUrl": "https://myagsserver.com:6443/arcgis/tokens/generateToken", // Optional, URL for token service; defaults to AGS token endpoint
    "site": {}, // Optional, directory structure for created site
    "json": {}, // Optional, specific parameters to use for all services, of all types.
    "mapServices": {
        "json": {}, // Optional, specific service parameters to use for all map services
        "services": [
            {
                "input": "mxd/my_map_document.mxd", // Required
                "output": "output/", // Optional, defaults to "output/"
                "serviceName": "MyMapDocument", // Optional, defaults to MXD filename, "my_map_document" here
                "serverType": "ARCGIS_SERVER", // Optional, defaults to "ARCGIS_SERVER"
                "copyDataToServer": "False", // Optional, defaults to False
                "folderName": "AutomationTests", // Optional, defaults to ""
                "summary": "Test map service published automagically", // Optional, defaults to ""
                "initialState": "STOPPED", // Optional, defaults to "STARTED"
                "workspaces": [ // Optional; defaults to *NOT* replace workspace paths
                    {
                        "old": {
                            "path": "c:/path/to/integration/connectionFile.sde", // Required if workspaces is defined
                            "type": "SDE_WORKSPACE" // Optional, defaults to SDE_WORKSPACE, for file geodatabase, use "FILEGDB_WORKSPACE"
                        },
                        "new": {
                            "path": "c:/path/to/production/connectionFile.sde", // Required if workspaces is defined
                            "type": "SDE_WORKSPACE" // Optional, defaults to SDE_WORKSPACE, for file geodatabase, use "FILEGDB_WORKSPACE"
                          }
                    }
                ],
                "json": {} // Optional, specific parameters for this service only
            }
        ]
    }
}
```

## Specifying service parameters
Service properties can be specified at multiple levels in the file; the most 
specific property will be used (i.e., service level, then type level, then 
global).  This allows for a minimum of configuration, while also allowing 
for service parameters to vary.  Note that the `json` parameter is identical 
what's specified in ESRI's [REST API](http://resources.arcgis.com/en/help/arcgis-rest-api/index.html#/Create_Service/02r3000001tr000000/). 
An example of the utilizing the `json` parameter is [enabling feature access](docs/publishfeatureservice.md) 
on a service.

## Example setup

### Continuous Integration Setup

First we need a basic directory structure, and a git repository:

```
mkdir myMapServices
cd myMapServices
git init
```

Now copy any MXDs into `myMapServices`; for this example, we'll assume we have two files, `Map1.mxd` and `Map2.mxd`.  To start with, we'll use a single configuration file, `config.json`.  
Once these are in place, the directory should look like this:

```
$ ls
Map1.mxd  Map2.mxd  config.json
```

Assuming we want to publish both services with schema locks disabled, our config file will look like:

``` json
{
    "agsUrl": "https://myagsserver.com:6443/arcgis/admin",
    "tokenUrl": "https://myagsserver.com:6443/arcgis/tokens/generateToken",
    "mapServices": {
        "json": {
            "properties": {
                "schemaLockingEnabled": false
            }  
        },
        "services": [
            {"input": "Map1.mxd"},
            {"input": "Map2.mxd"}
        ]
    }
}
```

Now on the CI server, we want to set a command something like this:

```
pip install slap
slap --config config.json --username <myUsername> --password <myPassword> --git
```

If you are using self-signed certs for AGS and/or Portal services, you will need to add those certs to your trusted store; see the [guide](docs/certs.md) for details.

### Deploying to a different environment

To publish the same set of services to a production environment, we'll create a new connection file, `prod.json`.  In our production environment, we want a few changes:

* A different set of connection files
* Schema locking to be *enabled*
* `maxIdleTime` to be 300ms, instead of the default 600

Our config file should look like:

``` json
{
    "agsUrl": "https://prodagsserver.com:6443/arcgis/admin",
    "tokenUrl": "https://prodagsserver.com:6443/arcgis/tokens/generateToken",
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
slap --config prod.json --username <myProductionUsername> --password <myProductionPassword> --all
```

## Integrating SLAP into another process

You can also [import SLAP](docs/importing.md) into a module and call it.

## Replacing workspace paths
To use separate credentials/data sources for different environments, you can supply an array of find/replace values under the `workspaces` key.  If this key is found,
the script will replace each `old` workspace path (i.e., path to a connection file) with the `new` value.

A few notes and caveats:

- Ideally, database connections will be via SDE, and use a connection file.  Sourcing from a File Geodatabase is also supported; 
  note that the FGDB will likely not be checked into version control. For file geodatabase, `"type": "FILEGDB_WORKSPACE"`
- If the FGDB sits on a share, consider using a UNC path rather than a drive letter, unless you are **sure** that the drive will always be mapped.
- For network shares (i.e., sourcing a FGDB), you *must* use JSON-escaped backslashes in the config (i.e., `\\`).  The `inputs` parameter should *not* add escapes (i.e., use `\`).
- It is possible to source from both an enterprise geodatabase(s) and file geodatabases(s) in the same MXD.

