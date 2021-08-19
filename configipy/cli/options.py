"""
Created 02-03-21 by Matt C. McCallum
"""


# Local imports
# None.

# Third party imports
import click

# Python standard library imports
# None.



#
# Options for several commands
#

def config(*args, **kwargs):

    def wrapper(func):
        return click.option(
            "--config", 
            "-c",
            help="Path to yaml configipy file for creation or processing", 
            **kwargs)(func)

    if args:
        return wrapper(args[0])
    return wrapper

def configurable(*args, **kwargs):

    def wrapper(func):
        return click.option(
            "--configurable", 
            "-f",
            help="Complete import path to configurable class in python import syntax, e.g., package.module.classname", 
            **kwargs)(func)

    if args:
        return wrapper(args[0])
    return wrapper

def param(*args, **kwargs):

    def wrapper(func):
        return click.option(
            "--param", 
            "-p",
            help="A value for a given option in the config", 
            **kwargs)(func)

    if args:
        return wrapper(args[0])
    return wrapper

def pymodule(*args, **kwargs):

    def wrapper(func):
        return click.option(
            "--pymodule", 
            "-m",
            help="Additional python packages / modules to import all from before running code.", 
            multiple=True,
            **kwargs)(func)

    if args:
        return wrapper(args[0])
    return wrapper