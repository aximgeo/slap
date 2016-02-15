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

    def test_get_root_keys(self):
        config = {
            'root_level': 'root',
            'mapServices': {
                'type_level': 'type',
                'services': [{
                    'input': 'map'
                }]
            }
        }
        self.assertEqual(self.m.get_root_keys(config), {'root_level': 'root'})

    def test_get_type_keys(self):
        config = {
            'root_level': 'root',
            'mapServices': {
                'type_level': 'type',
                'services': [{
                    'input': 'map'
                }]
            }
        }
        self.assertEqual(self.m.get_type_keys(config, 'mapServices'), {'type_level': 'type'})

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

    def test_flattening_nested_keys(self):
        config = {
            'root_level': 'root',
            'properties': {
                'myRootProp': 'someValue'
            },
            'mapServices': {
                'type_level': 'type',
                'properties': {
                    'myTypeProp': 'someOtherValue'
                },
                'services': [{
                    'input': 'map',
                    'properties': {
                        'myServiceProp': 'someThirdValue'
                    }
                }]
            }
        }
        self.assertEqual(self.m.parse_config(config)['mapServices']['services'][0], {
                                                             'input': 'map',
                                                             'root_level': 'root',
                                                             'type_level': 'type',
                                                             'properties': {
                                                                 'myRootProp': 'someValue',
                                                                 'myTypeProp': 'someOtherValue',
                                                                 'myServiceProp': 'someThirdValue'
                                                             }
                                                         })

    def check_missing_key(self, config):
        self.m.config = config
        with self.assertRaises(KeyError):
            self.m.check_required_keys()

    def test_raises_for_missing_connection_file_path(self):
        self.check_missing_key( {
            'mapServices': {
                'services': [{'input': 'foo'}]
            },
            'gpServices': {
                'services': []
            },
            'imageServices': {
                'services': []
            }
        })

    def test_raises_for_missing_input(self):
        self.check_missing_key( {
            'mapServices': {
                'services': [{'connectionFilePath': 'foo'}]
            },
            'gpServices': {
                'services': []
            },
            'imageServices': {
                'services': []
            }
        })
