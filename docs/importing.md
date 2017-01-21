# Importing SLAP into your existing code/module/project

It is also possible to import SLAP into your own process. Below we are 
globbing a directory for MXDs and sending them all to SLAP for 
publishing. This scenario works for when you have a folder structure full 
of production MXDs and a SLAP configuration file with all the MXDs in it 
and you want to perhaps replicate your services in another environment.

```python
from slap import publisher
import glob
import os

username = "user"
password = "pass"
slap_config = "path_to_config"

# Get list of input MXDs
inputs = glob.glob(os.path.join("path_to_mxds", "*.mxd"))

pub = publisher.Publisher()

print "Loading config..."
pub.load_config(slap_config)
pub.create_server_connection_file(username, password)
pub.init_api(
    ags_url=pub.config['agsUrl'],
    token_url=pub.config['tokenUrl'],
    portal_url=pub.config['portalUrl'] if 'portalUrl' in pub.config else None,
    certs=pub.config['certs'] if 'certs' in pub.config else True,
    username=username,
    password=password
)

for i in inputs:
    pub.publish_input(i)
```