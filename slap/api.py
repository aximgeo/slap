import urllib
import urllib2
import json


class Api(object):

    def __init__(self, ags_url, token_url, portal_url, username, password, certs=True):
        self._ags_url = ags_url
        self._token_url = token_url if token_url else ags_url + '/generateToken'
        self._portal_url = portal_url
        self._username = username
        self._password = password
        self._certs = certs  # Use system certs, unless we passed in a file path
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

    def _request(self, url, params, method):
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

    @staticmethod
    def build_folder_string(folder):
        return folder + '/' if folder else ''

    def build_params(self, params):
        params['f'] = 'json'
        params['token'] = self.token
        return params

