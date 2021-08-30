"""
Created 02-03-21 by Matt C. McCallum
"""

# Python standard library imports
import importlib
import textwrap

# Third party imports
import click
import ruamel.yaml

# Local imports
from . import options
import json


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
        from_x_import_all(module)
    print('\n')
    cfg = eval(f"{configurable}.CreateConfig(True)")
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
        from_x_import_all(module)
    subclss = eval(f"{configurable}._all_subclasses()")
    # TODO [matt.c.mccallum 02.03.21]: If there's no subclasses just print out the base class
    names = [sub.__name__ for sub in subclss]
    docs = [sub.__PARAM_DOCS__ for sub in subclss]
    result = ''
    for nm, dc in zip(names, docs):
        result += f'\n#\n# {nm}\n#\n'
        this_doc = dc.rstrip() + '\n\n'
        result += textwrap.indent(this_doc, '###', lambda x: True)
        # result += '\n'
    print(result)


def from_x_import_all(x):
    """
    """

    # get a handle on the module
    mdl = importlib.import_module(x)

    # is there an __all__?  if so respect it
    if "__all__" in mdl.__dict__:
        names = mdl.__dict__["__all__"]
    else:
        # otherwise we import all names that don't begin with _
        names = [name for name in mdl.__dict__ if not name.startswith("_")]

    # now drag them in
    globals().update({k: getattr(mdl, k) for k in names})


if __name__=='__main__':
    main()
