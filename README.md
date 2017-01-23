[![Build Status](https://travis-ci.org/gisinc/slap.svg?branch=master)](https://travis-ci.org/gisinc/slap)
[![Coverage Status](https://coveralls.io/repos/github/gisinc/slap/badge.svg?branch=master)](https://coveralls.io/github/gisinc/slap?branch=master)
[![PyPI version](https://badge.fury.io/py/slap.svg)](https://badge.fury.io/py/slap)

# SLAP Maps: Simple Library for Automated Publishing of Map Services

Command line tool for publishing map services

## Quick Setup
Install from pip using `pip install slap`

## Examples
* [Basic example](docs/basic-example.md)
* [Migrating services through environments (i.e. dev, test, prod)](docs/environment-transform.md)
* [Continous Integration](docs/continuous-integration.md)
* [Publishing Feature Services](docs/publish-feature-service.md)
* [Importing slap modules in Python scripts](docs/importing.md)

## Usage

Slap supports the following commands:

* [`init`](#init)
* [`publish`](#publish)

### init
Create a configuration file based on a directory; all arguments are optional.

```shell
usage: slap init [-h] [-c CONFIG] [-n NAME] [-r] [inputs [inputs ...]]
```

#### inputs
A list of directories to search for map documents when building the config; defaults to the current working directory.

#### -n, --name \<NAME>
Sets the hostname of the AGS server in config; defaults to `hostname`.

#### -c, --config \<CONFIG>
Overrides the default config file path and name; defaults to `config.json` in the current working directory.

#### -r, --register
Searches all map documents for data sources, and registers them with the geodatabase.

### publish
Publish services based on a configuration file

```
usage: slap publish [-h] -u USERNAME -p PASSWORD [-c CONFIG] [-g GIT] [-n NAME] [-s] [inputs [inputs ...]]
```

#### inputs
A list of map documents to publish; defaults to all documents listed in the config file.

#### -u, --username \<USERNAME>
Username for the AGS publisher account.

#### -p, --password \<PASSWORD>
Password for the AGS publisher account.

#### -c, --config \<CONFIG>
Path to the config file to use for publishing; defaults to `config.json` in the current working directory.

#### -g, --git \<COMMIT>
Republish all inputs that have changed since the previous commit; useful when publishing from a CI job.

#### -n, --name
Overrides the hostname of the AGS server in config; useful when publishing during a docker build.

#### -s, --site
Creates a new site before publishing; useful when publishing during a docker build.

## Config files
Configuration files are handled per-environment; for example, you might have three separate config files, `INT_config.json`, `UAT_config.json`, and `PROD_config.json`.
Each service is included in the config file as an object, grouped by service type.  *Note*:  Currently, only map services are supported.

An example configuration file might look like below.  *Note:* The comments would need to be removed, json is not valid with them.

```javascript
{
    "agsUrl": "https://myagsserver.com:6443/arcgis/admin", // Required, URL for AGS admin endpoint
    "tokenUrl": "https://myagsserver.com:6443/arcgis/tokens/generateToken", // Optional, URL for token service; defaults to AGS token endpoint
    "verifyCerts": "/path/to/certs.pem", // Optional, either True to use default store, False to not verify, or path to cert file. Defaults to False.
    "site": {}, // Optional, directory structure for creating a site
    "json": {}, // Optional, specific parameters to use for all services, of all types.
    "dataSources": [ // Optional, list of data items to add to the server store
        {
            "name": "slap-test",
            "serverPath": "slap-test.gdb",
            "clientPath": "slap-test.gdb"
        }
    ],
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

### Mixing in service parameters
Service properties can be specified at multiple levels in the file; the most 
specific property will be used (i.e., service level, then type level, then 
global).  This allows for a minimum of configuration, while also allowing 
for service parameters to vary.  Note that the `json` parameter is identical 
what's specified in ESRI's [REST API](http://resources.arcgis.com/en/help/arcgis-rest-api/index.html#/Create_Service/02r3000001tr000000/). 
An example of the utilizing the `json` parameter is [enabling feature access](docs/publish-feature-service.md) 
on a service.

### Replacing workspace paths
To use separate credentials/data sources for different environments, you can supply an array of find/replace values under the `workspaces` key.  If this key is found,
the script will replace each `old` workspace path (i.e., path to a connection file) with the `new` value.

## Required Artifacts
There are a few artifacts that need to be generated (via ArcMap) per service and/or environment, which are required for the process to run.  These can be checked into source control if desired, and pulled down as needed.

* MXD files: "Source" document for map services
* Database connection files: Needed per environment for publishing map services
* Config files: Needed per environment to specify publishing parameters
* Username/password: Credentials for publishing.  These are *not* specified in the configuration file, but are passed in at the command line.

## Contributing
We welcome feedback and contributions; please see the [contribution guide](CONTRIBUTING.md) for details