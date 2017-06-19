from builtins import object
import requests
import json


class Api(object):

    def __init__(self, ags_url, token_url, portal_url, username, password, verify_certs=False):
        self._ags_url = ags_url
        self._token_url = token_url if token_url else ags_url + '/generateToken'
        self._portal_url = portal_url
        self._username = username
        self._password = password
        self._verify_certs = verify_certs
        self._token = None

    @property
    def token(self):
        return self._token if self._token else self.get_token()

    @property
    def params(self):
        return {
            'token': self.token,
            'f': 'json'
        }

    def post(self, url, params):
        response = requests.post(url, data=params, verify=self._verify_certs)
        return self.parse_response(response)

    def get(self, url, params):
        response = requests.get(url, params=params, verify=self._verify_certs)
        return self.parse_response(response)

    @staticmethod
    def parse_response(response):
        if not response.ok:
            response.raise_for_status()

        parsed_response = response.json()
        Api.check_parsed_response(parsed_response)
        return parsed_response

    @staticmethod
    def check_parsed_response(parsed_response):
        if 'status' in parsed_response:  # token requests don't have this
            if parsed_response['status'] == 'error':  # handle a 200 response with an error
                raise requests.exceptions.RequestException(parsed_response['messages'][0])

    def get_token(self):
        params = {
            'username': self._username,
            'password': self._password,
            'client': 'requestip',
            'expiration': 60,
            'f': 'json'
        }
        response = self.post(self._token_url, params)
        self._token = response['token']
        return self._token

    def get_service_params(self, service_name, folder='', service_type='MapServer'):
        folder = self.build_folder_string(folder)
        url = '{0}/services/{1}{2}.{3}'.format(self._ags_url, folder, service_name, service_type)
        return self.get(url, self.params)

    def edit_service(self, service_name, params, folder='', service_type='MapServer'):
        folder = self.build_folder_string(folder)
        url = '{0}/services/{1}{2}.{3}/edit'.format(self._ags_url, folder, service_name, service_type)
        new_params = self.params.copy()
        new_params['service'] = json.dumps(params.copy())
        return self.post(url, new_params)

    def delete_service(self, service_name, folder='', service_type='MapServer'):
        folder = self.build_folder_string(folder)
        url = '{0}/services/{1}{2}.{3}/delete'.format(self._ags_url, folder, service_name, service_type)
        return self.post(url, self.params)

    def service_exists(self, service_name, folder='', service_type='MapServer'):
        url = '{0}/services/exists/exists'.format(self._ags_url)
        new_params = self.params.copy()
        new_params['folderName'] = folder
        new_params['serviceName'] = service_name
        new_params['type'] = service_type
        return self.post(url, new_params)

    def create_site(self, username, password, params):
        new_params = params.copy()
        new_params['username'] = username
        new_params['password'] = password
        new_params['confirmPassword'] = password
        new_params['f'] = 'json'
        return self.post('{0}/createNewSite'.format(self._ags_url), new_params)
    
    def create_default_site(self):
        return self.create_site(self._username, self._password, self.get_default_site_params())

    @staticmethod
    def get_default_site_params():
        # Set up required properties for config store
        config_store_path = '/home/arcgis/server/usr/config-store'
        config_store_connection = {'connectionString': config_store_path, 'type': 'FILESYSTEM'}

        # Set up paths for server directories
        # This will run in wine on linux, so we don't want os.path.separator here
        root_dir_path = '/home/arcgis/server/usr/directories'
        cache_dir_path = root_dir_path + '/arcgiscache'
        jobs_dir_path = root_dir_path + '/arcgisjobs'
        output_dir_path = root_dir_path + '/arcgisoutput'
        system_dir_path = root_dir_path + '/arcgissystem'

        # Create Python dictionaries representing server directories
        cache_dir = dict(
            name='arcgiscache',
            physicalPath=cache_dir_path,
            directoryType='CACHE',
            cleanupMode='NONE',
            maxFileAge=0,
            description='Stores tile caches used by map, globe, and image services for rapid performance.',
            virtualPath=''
        )
        jobs_dir = dict(
            name='arcgisjobs',
            physicalPath=jobs_dir_path,
            directoryType='JOBS',
            cleanupMode='TIME_ELAPSED_SINCE_LAST_MODIFIED',
            maxFileAge=360,
            description='Stores results and other information from geoprocessing services.',
            virtualPath=''
        )
        output_dir = dict(
            name='arcgisoutput',
            physicalPath=output_dir_path,
            directoryType='OUTPUT',
            cleanupMode='TIME_ELAPSED_SINCE_LAST_MODIFIED',
            maxFileAge=10,
            description='Stores various information generated by services, such as map images.',
            virtualPath=''
        )
        system_dir = dict(
            name='arcgissystem',
            physicalPath=system_dir_path,
            directoryType='SYSTEM',
            cleanupMode='NONE',
            maxFileAge=0,
            description='Stores files that are used internally by the GIS server.',
            virtualPath=''
        )

        # Serialize directory information to JSON
        directories = dict(directories=[cache_dir, jobs_dir, output_dir, system_dir])

        return {
            'configStoreConnection': json.dumps(config_store_connection, sort_keys=True),
            'directories': json.dumps(directories, sort_keys=True),
        }

    @staticmethod
    def build_folder_string(folder):
        return folder + '/' if folder else ''

    def build_params(self, params):
        params['f'] = 'json'
        params['token'] = self.token
        return params

