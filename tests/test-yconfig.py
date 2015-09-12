#!/usr/bin/env python

from __future__ import print_function
import os
import unittest
import sys


from yconfig import get_config, dict_format, dict_merge

CONF_DIR = "/tmp"
PREFIX = "asjflsdjasdlfvdnhq"
BASE_TEMPLATE_PATH = CONF_DIR + "/" + PREFIX + "_base.conf"
TEMPLATE_01_PATH = CONF_DIR + "/" + PREFIX + "_template01.conf"
TEMPLATE_02_PATH = CONF_DIR + "/" + PREFIX + "_template02.conf"
TEMPLATE_03_PATH = CONF_DIR + "/" + PREFIX + "_template03.conf"

DICT_FOR_FORMAT = {
    "1": {
        "1.1": ["one", "two", "three"],
        "1.2": {
            "1.2.1": "XXX {var3} XXX"
        }
    },
    "2": "{var1}",
    "3": ["{var2}", 4, "var"]
}

DICT1 = {
    "one": {
        "two": ["1", "2", "3"]
    },
    "two": {
        "three": {
            "four": "value_dict_1_four",
            "five": "value_dict_1_five"
        }
    },
    "three": "value_dict_1_3",
    "four": "XXX"
}

DICT2 = {
    "one": {
        "two": ["4", "5"]
    },
    "two": {
        "three": {
            "four": "XXX4",

        }
    },
    "three": "XXX3",
    "four": "XXX",
    "five": "XXX5"
}

CONF_TEMPLATE_BASE = """
uid: $#{os.getuid()}
"""

CONF_TEMPLATE_01 = """
$$import:
    - os

$$extends: "/tmp/asjflsdjasdlfvdnhq_base.conf"

colors:
    brown: "BROWN"
    yellow:
        light: "yellow"
        dark: "YELLOW"


fruits:
    apple: [ "red", "green", "$${colors.brown}", "yellow" ]
    banana:
        equador: "$${colors.yellow.dark}"
        columbia: $#{"red".upper()}
    uid: "process id: $${uid}"
"""

CONF_TEMPLATE_02 = """
$$import:
    - os

$$extends: "/tmp/asjflsdjasdlfvdnhq_base.conf"

colors:
    brown: "BROWN"
    yellow:
        light: "yellow"
        dark: "YELLOW"


fruits:
    apple: [ "red", "green", "$${colors.brown}", "yellow" ]
    banana:
        equador: "$${colors.yellow.dark}"
        columbia: $#{"red".upper()}
    uid: "process id: $#{uid}"
"""


CONF_TEMPLATE_03 = """
path:
    site_root: "/var/www/site-backend"
    template_dir: "$${path.site_root}/data/templates"
    email_templates_dir: "$${path.template_dir}/email"

test_path: "$${path.template_dir}/email"
"""

def write_file(fname, data):
    """Create file with data"""

    fd = open(fname, "w")
    fd.write(data)
    fd.close()


def read_file(fname):
    """Read data from file"""

    fd = open(fname, "r")
    data = fd.readlines()
    fd.close()

    return data


class YconfigTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        self.__test_dir = os.path.dirname(__file__)
        self.do_teardown = True
        self.stdout = sys.stdout
        self.stderr = sys.stderr

    def setUp(self):
        """Init tests"""

        self.do_teardown = True
        write_file(BASE_TEMPLATE_PATH, CONF_TEMPLATE_BASE)
        write_file(TEMPLATE_01_PATH, CONF_TEMPLATE_01)
        write_file(TEMPLATE_02_PATH, CONF_TEMPLATE_02)
        write_file(TEMPLATE_03_PATH, CONF_TEMPLATE_03)

    def tearDown(self):
        """Cleanup tests"""

        if self.do_teardown:
            for f in os.listdir(CONF_DIR):
                if f.startswith(PREFIX):
                    try:
                        os.remove(CONF_DIR + "/" + f)
                    except:
                        pass

            # try:
            #     os.remove(LOG_CONF_PATH_DEFAULTS)
            # except:
            #     pass

    def test_010_get_config(self):
        """010 Test config file reading"""

        conf = get_config(TEMPLATE_01_PATH)

        uid = os.getuid()

        self.assertTrue("uid" in conf.keys())

        self.assertEqual(uid, int(conf.uid))
        self.assertEqual(conf.fruits.uid, "process id: {0}".format(uid))
        self.assertEqual(conf.fruits.banana.equador, "YELLOW")
        self.assertEqual(conf.fruits.apple[2], "BROWN")

    def test_015_get_config_with_globals(self):
        """015 Test config file reading with _globals"""

        uid = os.getuid()
        conf = get_config(TEMPLATE_02_PATH, _globals={"uid":uid})

        self.assertTrue("uid" in conf.keys())

        self.assertEqual(uid, int(conf.uid))

    def test_020_dict_format(self):
        """020 Test dict_formatting"""

        d = dict_format(DICT_FOR_FORMAT, {
            "var1": "test1",
            "var2": "test2",
            "var3": "test3",
        })

        self.assertEqual(d["1"]["1.2"]["1.2.1"], "XXX test3 XXX")
        self.assertEqual(d["2"], "test1")
        self.assertEqual(d["3"][0], "test2")

    def test_030_dict_merge(self):
        """030 Test dict merging"""

        d = dict_merge(DICT1, DICT2)

        self.assertEqual(d["one"]["two"], ["4", "5"])
        self.assertEqual(d["two"]["three"]["four"], "XXX4")
        self.assertEqual(d["two"]["three"]["five"], "value_dict_1_five")
        self.assertEqual(d["three"], "XXX3")
        self.assertEqual(d["four"], "XXX")
        self.assertEqual(d["five"], "XXX5")

    def test_040_eval_conf_variables(self):
        """040 Test config variables evaluating"""

        conf = get_config(TEMPLATE_03_PATH)

        self.assertEqual(conf.path.site_root + '/data/templates/email', conf.test_path)
        self.assertEqual(conf.path.site_root + '/data/templates/email', conf.path.email_templates_dir)

if __name__ == "__main__":
    unittest.main()
