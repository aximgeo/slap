import requests
import wincertstore

class Api:

    _ags_url = None
    _token_url = None
    _portal_url = None
    _username = None
    _password = None
    _token = None
    _certs = None

    def __init__(self, ags_url, token_url, portal_url, username, password):
        self._ags_url = ags_url
        self._token_url = token_url if token_url else ags_url + '/generateToken'
        self._portal_url = portal_url
        self._username = username
        self._password = password
        self._certs = wincertstore.CertFile()
        self._certs.addcerts('ROOT')
        self._certs.addcerts('CA')

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
        return self._request(requests.post, url, params)

    def get(self, url, params):
        return self._request(requests.get, url, params)

    def _request(self, request_method, url, params):
        response = request_method(url, params=params, verify=self._certs.name)

        if response.status_code != requests.codes.ok:
            response.raise_for_status()

        parsed_response = response.json()
        if parsed_response['status'] == 'error':  # handle a 200 response with an error
            raise requests.exceptions.RequestException(parsed_response['messages'][0])

        return parsed_response

    def get_token(self):
        params = {
            'username': self._username,
            'password': self._password,
            'f': 'json'
        }
        response = self.get(self._token_url, params)
        return response['token']

    def get_service_params(self, service_name, folder='', service_type='MapServer'):
        folder = folder + '/' if folder else ''
        url = '{0}/services/{1}{2}.{3}'.format(self._ags_url, folder, service_name, service_type)
        return self.get(url, self.params)

    def edit_service(self, service_name, params, folder='', service_type='MapServer'):
        folder = folder + '/' if folder else ''
        url = '{0}/services/{1}{2}.{3}/edit'.format(self._ags_url, folder, service_name, service_type)
        params['f'] = 'json'
        params['token'] = self.token
        return self.post(url, params)

    def delete_service(self, service_name, folder=''):
        folder = folder + '/' if folder else ''
        url = '{0}/services/{1}{2}/delete'.format(self._ags_url, folder, service_name)
        return self.post(url, self.params)

