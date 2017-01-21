# Continuous Integration Setup

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
