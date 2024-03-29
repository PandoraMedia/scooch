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
# None.

# Third party imports
import click

# Local imports
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
        help="Path to yaml scooch file for creation or processing"
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

param = partial_option(
        "--param",
        help="Custom parameter override option to replace values in a config.yml file.",
        multiple=True,
    )
