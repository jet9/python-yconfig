"""YAML-based configuration file processing

- use YAML format for config files
- use $#{python_expr} as values to evaluate python expressions:

    variable: $#{3+5}
    # variable = 8

    uid = $#{os.getuid()}
    # uid = current uid
    # WARNING: You should import modules os in template for evaluating this expression.
    # See next for details

- use `$$import` in root of config file to import python modules:

    $$import:
        - os.path
        - sys

    # get current program name without extension
    current_program_name: $#{os.path.splitext(os.path.basename(sys.argv[0]))[0]}

- use `$$extends` in root of config file to extend other templates:

    # this config will be read from /path/to/base.conf and next structure
    # will replace `some.variable.to.replace` with new value

    $$extends: "/path/to/base.conf"

    some:
        variable:
            to:
                replace: "some value"

- use `$$variable_name` in config values to replace it with variable values:

    some:
        value: "XXX"
        value2: "ZZZ"

    struct:
        user: "root"
        value: $${some.value}
        msg: "Some value $${some.value2} inside a string"
"""

import yaml
import re
# import logging as LOG

from copy import deepcopy
from ndict import NDict

# LOG.basicConfig(format='%(levelname)s: %(message)s', level=LOG.ERROR)
# TODO: remove debugging code

__version__ = "0.2"
_var_pattern = re.compile(r"\$\$\{([a-zA-Z0-9_\.]+)\}")
_expr_pattern = re.compile(r"\$#\{(.+)\}")
_python_var_pattern = re.compile(r"{([a-zA-Z0-9_]+)}")
"""Regexp pattern for search {variables}"""


def _load_config(fname):
    """load config file"""

    return NDict(yaml.load(open(fname)))


def _extends_config(conf):
    """"Recursively extends config"""

    if "$$extends" in conf.keys():
        # LOG.debug("$$extends found: {0}".format(conf["$$extends"]))
        e_conf = _load_config(conf["$$extends"])
        if "$$import" in e_conf.keys() and "$$import" in conf.keys():
            # LOG.debug("$$import found in both config")
            conf["$$import"].extend(e_conf["$$import"])
            # LOG.debug("imports: {0}".format(conf["$$import"]))

        if "$$extends" in e_conf.keys() and "$$extends" in conf.keys():
            # LOG.debug("$$extends found in both config")
            conf["$$extends"] = e_conf["$$extends"]
            # LOG.debug("extends: {0}".format(e_conf["$$extends"]))
        else:
            del conf["$$extends"]

        e_conf = dict_merge(e_conf, conf)
        conf = _extends_config(e_conf)

    return conf


def dict_merge(a, b):
    """Recursively merges dict's. not just simple a['key'] = b['key'], if
    both a and bhave a key who's value is a dict then dict_merge is called
    on both values and the result stored in the returned dictionary."""

    if not isinstance(b, dict):
        return b
    result = deepcopy(a)
    for k, v in b.iteritems():
        if k in result and isinstance(result[k], dict):
                result[k] = dict_merge(result[k], v)
        else:
            result[k] = deepcopy(v)
    return result


def __custom_format(_str, values):
    """Custom format routine with basic functionality"""

    for var in _python_var_pattern.findall(_str):
        if var in values.keys():
            _str = _str.replace("{" + var + "}", values[var])

    return _str


def dict_format(obj, values):
    """Simple recursive formatter for value strings in generic object(str, list, dict)

    @obj: [str, list, dict]:   obj that will be formatted
    @values: dict:  dict with values for format()"""

    if isinstance(obj, dict):
        for k in obj.keys():
            obj[k] = dict_format(obj[k], values)
    if isinstance(obj, list):
        for k in obj:
            obj[obj.index(k)] = dict_format(k, values)
    elif isinstance(obj, str):
        # _dict[k] = v.format(**values)
        return __custom_format(obj, values)

    return obj


def _import_modules(import_list):
    """import modules"""

    for item in import_list:
        # LOG.info("import {0}".format(item))
        globals()[item.split(".")[0]] = __import__(item)


def _process_root_keys(conf):
    """Process uniq key in dict"""

    if "$$extends" in conf.keys():
        # LOG.debug("Process $$extends")
        conf = _extends_config(conf)

    if "$$import" in conf.keys():
        # LOG.debug("Process $$import")
        _import_modules(conf["$$import"])

    return conf


def _eval_python_str(value, _globals=None):
    """Evaluate python source str"""

    if _globals is None:
        _globals = {}

    _globals.update(globals())
    for subs in _expr_pattern.findall(value):
        eval_expr = eval(subs, _globals)
        # LOG.info("evaluate python: {0} -> {1}".format(subs, eval_expr))
        # LOG.info("value: {0}".format(value))
        # LOG.info("replace: {0} -> {1}".format("$#{"+subs+"}", eval_expr))

        value = value.replace("$#{" + subs + "}", str(eval_expr))

    return value


def _eval_conf_str(tree, value, _globals=None):
    """Evaluate internal config variable"""

    # LOG.info("evaluate internal conf str: {0}".format(value))
    for subs in _var_pattern.findall(value):
        eval_var = eval("tree." + subs)
        if isinstance(eval_var, str) and eval_var.find("$#") != -1:
            eval_var = _eval_python_str(eval_var, _globals=_globals)
        # LOG.info("replace: {0} -> {1}".format(subs, eval_var))
        value = value.replace("$${" + subs + "}", str(eval_var))

    return value


def _evaluate_obj(tree, item, _globals=None):
    """bypass config tree and apply templater to key/values"""

    if isinstance(item, dict):
        for k in item.keys():
            item[k] = _evaluate_obj(tree, item[k], _globals=_globals)

    elif isinstance(item, list):
        for k in item:
            item[item.index(k)] = _evaluate_obj(tree, k, _globals=_globals)

    elif isinstance(item, str):
        if item.find("$$") != -1:
            # LOG.debug("find subs '$$' in '{0}'".format(item))
            item = _eval_conf_str(tree, item, _globals=_globals)

        if item.startswith("$#"):
            return _eval_python_str(item, _globals=_globals)

    else:
        # LOG.warn("Unknown obj instance: {0}".format(type(item)))
        pass

    return item


def _process_config(conf, _globals=None):
    """process config template"""

    conf = _process_root_keys(conf)

    return _evaluate_obj(conf, conf, _globals=_globals)


def get_config(fname, _globals=None):
    """Get config from filename"""

    conf = _load_config(fname)

    return _process_config(conf, _globals=_globals)


if __name__ == "__main__":
    # small usage example
    # from pprint import pprint
    # import sys

    # sys.exit(0)

    # sys.path.append("../common")
    # conf = get_config("/etc/c2/logging/defaults.conf")
    # pprint(conf)
    pass
