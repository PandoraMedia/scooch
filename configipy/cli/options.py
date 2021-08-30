"""
Created 02-03-21 by Matt C. McCallum
"""


# Local imports
# None.

# Third party imports
import click

# Python standard library imports
# None.


def partial_option(*args, **kwargs):
    option = click.option(*args, **kwargs)

    def option_decorator(command=None):
        if command:
            # We were used as a decorator without arguments, and now we're being
            # called on the command function.
            return option(command)
        else:
            # We are being called with empty parens to construct a decorator.
            return option

    return option_decorator

#
# Options for several commands
#
config = partial_option(
        "--config", 
        "-c",
        help="Path to yaml configipy file for creation or processing"
    )

configurable = partial_option(
        "--configurable", 
        "-f",
        help="Complete import path to configurable class in python import syntax, e.g., package.module.classname", 
    )

pymodule = partial_option(
        "--pymodule", 
        "-m",
        help="Additional python packages / modules to import all from before running code.", 
        multiple=True,
)
