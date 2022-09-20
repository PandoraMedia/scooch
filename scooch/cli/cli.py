# coding=utf-8
# Copyright 2021 Pandora Media, LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# Python standard library imports
import importlib
import textwrap

# Third party imports
import click
import ruamel.yaml

# Local imports
from . import options
import json
from scooch import Configurable
from scooch import ConfigFactory


@click.group()
def main():
    pass


@main.command()
@options.config
@options.configurable
@options.pymodule
def construct(config, configurable, pymodule):
    """
    Constructs a Config as a yaml file, for a given Configurable in a given module.
    """
    for module in pymodule:
        importlib.import_module(module)
    print('\n')
    try:
        configurable = next(x for x in Configurable._all_subclasses() if x.__name__ == configurable)
    except StopIteration:
        print(f"Error: No Configurable named {configurable} found (after importing: {pymodule})")
        return
    cfg = ConfigFactory(True).create_config(configurable)
    if config != None and len(config) > 0:
        with open(config, 'w') as f:
            ruamel.yaml.YAML().dump(cfg, f)
    else:
        print(json.dumps(cfg, indent=4, sort_keys=True))


@main.command()
@options.configurable
@options.pymodule
def options(configurable, pymodule):
    """
    Prints out all sub configurables for a given parent configurable.
    """
    for module in pymodule:
        importlib.import_module(module)
    try:
        configurable = next(x for x in Configurable._all_subclasses() if x.__name__ == configurable)
    except StopIteration:
        print(f"Error: No Configurable named {configurable} found (after importing: {pymodule})")
        return
    subclss = configurable._all_subclasses() + [configurable]
    # TODO [matt.c.mccallum 02.03.21]: If there's no subclasses just print out the base class
    names = [sub.__name__ for sub in subclss]
    docs = [sub.__doc__ for sub in subclss]
    result = ''
    for nm, dc in zip(names, docs):
        result += f'\n#\n# {nm}\n#\n'
        this_doc = dc.rstrip() + '\n\n'
        result += textwrap.indent(this_doc, '###', lambda x: True)
    print(result)


if __name__=='__main__':
    main()
