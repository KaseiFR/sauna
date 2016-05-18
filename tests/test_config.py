import copy
import unittest
try:
    from unittest import mock
except ImportError:
    # Python 3.2 does not have mock in the standard library
    import mock

from sauna import Sauna, _merge_config


class ConfigTest(unittest.TestCase):

    def test_dict_conf(self):
        dict_conf = {
            "plugins": {
                "Disk": {
                    "config": {
                        "myconf": "myvalue"
                    },
                    "checks": [
                        {
                            "type": "used_percent",
                            "warn": "80%",
                            "crit": "90%"
                        }
                    ]
                }
            }
        }
        expected_result = [
            {
                'type': 'Disk',
                "config": {
                    "myconf": "myvalue"
                },
                "checks": [
                    {
                        "type": "used_percent",
                        "warn": "80%",
                        "crit": "90%"
                    }
                ]
            }
        ]
        sauna = Sauna(config=dict_conf)
        self.assertEqual(sauna.plugins_checks, expected_result)

    def test_list_conf(self):
        list_conf = {
            "plugins": [
                {
                    'type': 'Disk',
                    "config": {
                        "myconf": "myvalue"
                    },
                    "checks": [
                        {
                            "type": "used_percent",
                            "warn": "80%",
                            "crit": "90%"
                        }
                    ]
                }
            ]
        }

        sauna = Sauna(config=list_conf)
        self.assertEqual(sauna.plugins_checks, list_conf['plugins'])

    def test_complex_dict_conf(self):
        dict_conf = {
            "plugins": {
                "Disk": {
                    "config": {
                        "myconf": "myvalue"
                    },
                    "checks": [
                        {
                            "type": "used_percent",
                            "warn": "80%",
                            "crit": "90%"
                        },
                        {
                            "type": "used_percent",
                            "warn": "80%",
                            "crit": "90%"
                        }
                    ]
                },
                "Memory": {
                    "config": {
                        "myconf": "myvalue"
                    },
                    "checks": [
                        {
                            "type": "used_percent",
                            "warn": "80%",
                            "crit": "90%"
                        },
                    ]
                }
            }
        }
        expected_result = [
            {
                'type': 'Disk',
                "config": {
                    "myconf": "myvalue"
                },
                "checks": [
                    {
                        "type": "used_percent",
                        "warn": "80%",
                        "crit": "90%"
                    },
                    {
                        "type": "used_percent",
                        "warn": "80%",
                        "crit": "90%"
                    }
                ]
            },
            {
                "type": "Memory",
                "config": {
                    "myconf": "myvalue"
                },
                "checks": [
                    {
                        "type": "used_percent",
                        "warn": "80%",
                        "crit": "90%"
                    },
                ]
            }
        ]
        sauna = Sauna(config=dict_conf)
        self.assertEqual(len(sauna.plugins_checks), len(expected_result))
        for elem in sauna.plugins_checks:
            self.assertIn(elem, expected_result, 'missing element')

    def test_merge_config(self):
        original = {
            'periodicity': 60,
            'consumers': {
                'Stdout': {}
            },
            'plugins': [
                {
                   'type': 'Disk',
                   "config": {
                       "myconf": "myvalue"
                   },
                   "checks": [
                       {
                           "type": "used_percent",
                           "warn": "80%",
                           "crit": "90%"
                       },
                       {
                           "type": "used_percent",
                           "warn": "80%",
                           "crit": "90%"
                       }
                   ]
                }
            ]
        }

        # Not changing anthing
        expected = copy.deepcopy(original)
        _merge_config(original, {})
        self.assertDictEqual(original, expected)

        # Adding a consumer
        expected['consumers']['NSCA'] = {}
        _merge_config(original, {'consumers': {'NSCA': {}}})
        self.assertDictEqual(original, expected)

        # Adding a plugin
        expected['plugins'].append({'type': 'Load'})
        _merge_config(original, {'plugins': [{'type': 'Load'}]})
        self.assertDictEqual(original, expected)

        # Adding a root property
        expected['hostname'] = 'host-1.domain.tld'
        _merge_config(original, {'hostname': 'host-1.domain.tld'})
        self.assertDictEqual(original, expected)

        # Appending to a non existent list
        expected['extra_plugins'] = ['/opt/plugins1', '/opt/plugins2']
        _merge_config(original,
                      {'extra_plugins': ['/opt/plugins1', '/opt/plugins2']})
        self.assertDictEqual(original, expected)
