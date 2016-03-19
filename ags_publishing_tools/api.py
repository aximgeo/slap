import urllib
import urllib2
import json
import codecs


class Api:

    _ags_url = None
    _token_url = None
    _portal_url = None
    _username = None
    _password = None
    _token = None
    _certs = None

    def __init__(self, ags_url, token_url, portal_url, username, password, certs=True):
        self._ags_url = ags_url
        self._token_url = token_url if token_url else ags_url + '/generateToken'
        self._portal_url = portal_url
        self._username = username
        self._password = password
        self._certs = certs  # Use system certs, unless we passed in a file path

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
        encoded_params = urllib.urlencode(params)
        print "Params:", params
        if method == 'GET':
            request = urllib2.Request(url + '?' + encoded_params)
            request.get_method = lambda: method
            response = urllib2.urlopen(request)
        else:
            request = urllib2.Request(url)
            request.get_method = lambda: method
            # request.add_header('Content-Type', 'application/json')
            response = urllib2.urlopen(request, encoded_params)

        reader = codecs.getreader("utf-8")
        parsed_response = json.load(reader(response))
        print parsed_response
        # response_text = response.readall().decode('utf-8')
        # print "Response:", response_text
        # parsed_response = json.loads(response_text)

        if 'status' in parsed_response and parsed_response['status'] == 'error':  # handle a 200 response with an error
            raise urllib2.URLError(parsed_response['status'] + ','.join(parsed_response['messages']))

        return parsed_response

    def get_token(self):
        params = {
            'username': self._username,
            'password': self._password,
            'client': 'referer',
            'referer': self._ags_url,
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
        new_params = params.copy()
        new_params.update(self.params)
        return self.post(url, new_params)

    def delete_service(self, service_name, folder='', service_type='MapServer'):
        folder = self.build_folder_string(folder)
        url = '{0}/services/{1}{2}.{3}/delete'.format(self._ags_url, folder, service_name, service_type)
        return self.post(url, self.params)

    @staticmethod
    def build_folder_string(folder):
        return folder + '/' if folder else ''

    def build_params(self, params):
        params['f'] = 'json'
        params['token'] = self.token
        return params

