python-yconfig
==============

Yet Another YAML configuration files manager for python

YAML-based configuration file processing

- use YAML format for config files
- use `$#{python_expr}` as values to evaluate python expressions:

```(yaml)
variable: $#{3+5}
# variable = 8

uid = $#{os.getuid()}
# uid = current uid
# WARNING: You should import modules os in template for evaluating this expression.
# See next for details
```

- use `$$import` in root of config file to import python modules:

```(yaml)
$$import:
    - os.path
    - sys

# get current program name without extension
current_program_name: $#{os.path.splitext(os.path.basename(sys.argv[0]))[0]}
```

- use `$$extends` in root of config file to extend other templates:

```(yaml)
# this config will be read from /path/to/base.conf and next structure
# will replace `some.variable.to.replace` with new value

$$extends: "/path/to/base.conf"

some:
    variable:
        to:
            replace: "some value"
```

- use `$$variable_name` in config values to replace it with variable values:

```(yaml)
some:
    value: "XXX"
    value2: "ZZZ"

struct:
    user: "root"
    value: $${some.value}
    msg: "Some value $${some.value2} inside a string"
```