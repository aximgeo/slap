import os
import urllib
import urllib2
import json


class Api:

    def __init__(self, ags_url, token_url, portal_url, username, password):
        self._ags_url = ags_url
        self._token_url = token_url if token_url else ags_url + '/generateToken'
        self._portal_url = portal_url
        self._username = username
        self._password = password
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
        return self._request(url, params, 'POST')

    def get(self, url, params):
        return self._request(url, params, 'GET')

    @staticmethod
    def _request(url, params, method):
        encoded_params = urllib.urlencode(json.loads(json.dumps(params)))
        request = urllib2.Request(url + '?' + encoded_params) if method == 'GET' else urllib2.Request(url, encoded_params)
        request.get_method = lambda: method
        response = urllib2.urlopen(request)
        parsed_response = json.loads(response.read())

        if 'status' in parsed_response and parsed_response['status'] == 'error':  # handle a 200 response with an error
            raise urllib2.URLError(parsed_response['status'] + ','.join(parsed_response['messages']))

        return parsed_response

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
        return self.post('{0}/createSite'.format(self._ags_url), params)
    
    def create_default_site(self):
        return self.create_site(self._username, self._password, self.get_default_site_params())

    @staticmethod
    def get_default_site_params():

        config_store_path = '/home/arcgis/server/usr/config-store'
        root_dir_path = '/home/arcgis/server/usr/directories'

        # Set up required properties for config store
        config_store_connection = {'connectionString': config_store_path, 'type': 'FILESYSTEM'}

        # Set up paths for server directories
        cache_dir_path = os.path.join(root_dir_path, 'arcgiscache')
        jobs_dir_path = os.path.join(root_dir_path, 'arcgisjobs')
        output_dir_path = os.path.join(root_dir_path, 'arcgisoutput')
        system_dir_path = os.path.join(root_dir_path, 'arcgissystem')

        # Create Python dictionaries representing server directories
        cache_dir = dict(name='arcgiscache', physicalPath=cache_dir_path, directoryType='CACHE', cleanupMode='NONE',
                         maxFileAge=0,
                         description='Stores tile caches used by map, globe, and image services for rapid performance.',
                         virtualPath='')
        jobs_dir = dict(name='arcgisjobs', physicalPath=jobs_dir_path, directoryType='JOBS',
                        cleanupMode='TIME_ELAPSED_SINCE_LAST_MODIFIED', maxFileAge=360,
                        description='Stores results and other information from geoprocessing services.', virtualPath='')
        output_dir = dict(name='arcgisoutput', physicalPath=output_dir_path, directoryType='OUTPUT',
                          cleanupMode='TIME_ELAPSED_SINCE_LAST_MODIFIED', maxFileAge=10,
                          description='Stores various information generated by services, such as map images.',
                          virtualPath='')
        system_dir = dict(name='arcgissystem', physicalPath=system_dir_path, directoryType='SYSTEM', cleanupMode='NONE',
                          maxFileAge=0, description='Stores files that are used internally by the GIS server.',
                          virtualPath='')

        # Serialize directory information to JSON
        directories_json = json.dumps(dict(directories=[cache_dir, jobs_dir, output_dir, system_dir]))

        return {
            'configStoreConnection': config_store_connection,
            'directories': directories_json,
            'f': 'json'
        }

    @staticmethod
    def build_folder_string(folder):
        return folder + '/' if folder else ''

    def build_params(self, params):
        params['f'] = 'json'
        params['token'] = self.token
        return params

