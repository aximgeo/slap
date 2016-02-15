import os
import unittest
from unittest import TestCase
from ags_publishing_tools.ConfigParser import ConfigParser


class TestConfigParser(TestCase):
    m = None

    def setUp(self):
        self.m = ConfigParser()

    def test_empty_config(self):
        self.assertEqual(self.m.parse_config({}), {
            'mapServices': {
                'services': []
            },
            'gpServices': {
                'services': []
            },
            'imageServices': {
                'services': []
            }
        })

    def test_no_map_services(self):
        config = {
            'gpServices': {
                'services': [{'input': 'gp'}]
            },
            'imageServices': {
                'services': [{'input': 'image'}]
            }
        }
        self.assertEqual(self.m.parse_config(config), {
            'mapServices': {
                'services': []
            },
            'gpServices': {
                'services': [{'input': 'gp'}]
            },
            'imageServices': {
                'services': [{'input': 'image'}]
            }
        })

    def test_no_gp_services(self):
        config = {
            'mapServices': {
                'services': [{'input': 'map'}]
            },
            'imageServices': {
                'services': [{'input': 'image'}]
            }
        }
        self.assertEqual(self.m.parse_config(config), {
            'mapServices': {
                'services': [{'input': 'map'}]
            },
            'gpServices': {
                'services': []
            },
            'imageServices': {
                'services': [{'input': 'image'}]
            }
        })

    def test_no_image_services(self):
        config = {
            'gpServices': {
                'services': [{'input': 'gp'}]
            },
            'mapServices': {
                'services': [{'input': 'map'}]
            }
        }
        self.assertEqual(self.m.parse_config(config), {
            'mapServices': {
                'services': [{'input': 'map'}]
            },
            'gpServices': {
                'services': [{'input': 'gp'}]
            },
            'imageServices': {
                'services': []
            }
        })

    def test_get_extra_keys(self):
        config = {
            'root_level': 'root',
            'mapServices': {
                'type_level': 'type',
                'services': [{
                    'input': 'map'
                }]
            }
        }
        self.assertEqual(self.m.get_non_type_keys(config, 'mapServices'), {
                                                             'root_level': 'root',
                                                             'type_level': 'type'
        })

    def test_flattening_keys(self):
        config = {
            'root_level': 'root',
            'mapServices': {
                'type_level': 'type',
                'services': [{
                    'input': 'map'
                }]
            }
        }
        self.assertEqual(self.m.parse_config(config)['mapServices']['services'][0], {
                                                             'input': 'map',
                                                             'root_level': 'root',
                                                             'type_level': 'type'
                                                         }
                         )

class TestSdDraftParser_properties(TestCase):
    m = None

    def setUp(self):
        self.m = ConfigParser()
        self.m.config = {
            'properties': {
                'foo': 'bar',
                'baz': 'quux'
            },
            'mapServices': {
                'services': [
                    {
                        'input': '1stInput',
                    },
                    {
                        'input': '2ndInput',
                        'properties': {
                            'foo': 'newFoo'
                        }
                    }
                ]
            }
        }

class TestSdDraftParser_connection_file_path(TestCase):
    m = None

    def setUp(self):
        self.m = ConfigParser()
        self.m.config = {
            'connectionFilePath': 'my/connection',
            'mapServices': {
                'services': [
                    {
                        'input': 'foo'
                    }
                ]
            }
        }

    def connection_file_paths_match(self, path, config):
        self.assertEqual(os.getcwd() + '\\' +  path, self.m.get_connection_file_path('mapServices', config))


    def test_get_top_level_connection_file_path(self):
        self.connection_file_paths_match('my/connection', {'input': 'foo'})


    def test_get_type_level_connection_file_path(self):
        self.m.config = {
            'mapServices': {
                'connectionFilePath': 'my/type/connection',
                'services': [
                    {
                        'input': 'foo'
                    }
                ]
            }
        }
        self.connection_file_paths_match('my/type/connection', {'input': 'foo'})


    def test_get_service_level_connection_file_path(self):
        self.m.config = {
            'mapServices': {
                'services': [
                    {
                        'input': 'foo',
                        'connectionFilePath': 'my/service/connection'
                    }
                ]
            }
        }
        self.connection_file_paths_match('my/service/connection', {
            'input': 'foo',
            'connectionFilePath': 'my/service/connection'
        })
