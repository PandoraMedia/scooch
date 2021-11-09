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
import os
import json
import hashlib
import re
from datetime import datetime

# Third party module imports
import yaml

# Local imports
# None.


# NOTE [matt.c.mccallum 03.19.20]: The below constant is evaluated at module import time and
#      is required because datetime objects have trouble being pickled and sent to other machines
#      with other clock systems. The constant, evaluated at module import time, however, can
#      be pickled and distributed.
CURRENT_DATETIME = datetime.now().strftime("%Y%m%d_%H%M%S")


class Config(dict):
    """
    A simple class that encapsulates feature configuration files stored in yaml format.
    Each feature configuration file should contain all the details that make a feature unique for a certain type, e.g.,
    a CQT.
    """

    # TODO [matt.c.mccallum 07.03.19]: Allow loading a whole folder of configs
    # TODO [matt.c.mccallum 07.03.19]: Allow linking or references between configs to avoid duplication

    def __init__(self, config_file):
        """
        **Constructor.**

        Args:
            config_file: str, dict, file or Config - A file like object or filename describing a yaml file to load
            this class's configuration from. Alternatively, it can be a dictionary describing the 
        """
        if type(config_file) is str:
            with open(config_file) as f:
                self.update(yaml.safe_load(f))
        elif isinstance(config_file, dict):
            self.update(config_file)
        else:
            self.update(yaml.safe_load(config_file))

        # Store any variables
        if isinstance(config_file, Config):
            self._vars = config_file._vars
        else:
            self._vars = self.get('Constants', [])
            if len(self._vars):
                del self['Constants']

        self._VAR_FUNCS = {
            'inherit': Config._inherit,
            'datetime': Config._datetime
        }

        self._evaluate_vars(self)

    @classmethod
    def _inherit(cls, heirarchy, term, value):
        """
        Macro function to inherit a value from identical keys in it's parent dictionar(ies).

        Args:
            heirarchy: dict - The dictionary heirarchy containing the key and value pair
            that in turn contain a macro function.

            term: str - The dictionary key that the macro occurs at.

            value: str - The string containing the macro expression.

        Return:
            value: str - The provided value with the macro expression evaluated.
        """
        if 'PARENT' not in heirarchy.keys():
            raise KeyError('No inheritable attribute "{}" found in Scooch heirarchy'.format(term))
        return cls._inherit_recurse(heirarchy['PARENT'], term, value)

    @classmethod
    def _inherit_recurse(cls, heirarchy, term, value):
        """
        Recurses through all parent dicitonaries to find a matching key with whoms value
        to use to replace the provided value.

        See Config._inherit for details.
        """
        for child in heirarchy.keys():
            if child == term:
                return heirarchy[child]
        if 'PARENT' in heirarchy.keys():
            return cls._inherit_recurse(heirarchy['PARENT'], term, value)
        else:
            raise KeyError('No inheritable attribute "{}" found in Scooch heirarchy'.format(term))

    @classmethod
    def _datetime(cls, heirarchy, term, value):
        """
        Macro function to insert a datetime substring into the variable.

        Args:
            heirarchy: dict - The dictionary heirarchy containing the key and value pair
            that in turn contain a macro function.

            term: str - The dictionary key that the macro occurs at.

            value: str - The string containing the macro expression.

        Return:
            value: str - The provided value with the macro expression evaluated.
        """
        value = value.replace(r'${datetime}', CURRENT_DATETIME)
        return value

    def _evaluate_macro(self, heirarchy, term, value):
        """
        Evaluates all macros in the provided value.

        Args:
            heirarchy: dict - The dictionary heirarchy containing the key and value pair
            that in turn contain a macro function.

            term: str - The dictionary key that the macro occurs at.

            value: str - The string containing the macro expression.

        Return:
            value: str - The provided value with the macro expression evaluated.
        """
        while type(value) is str and len(re.findall(r'\$\{(.*?)\}', value)):
            func_name = re.findall(r'\$\{(.*?)\}', value)[0]  # NOTE [matt.c.mccallum 02.14.20]: Double evaluation of regex here, not the most efficient, but we're less concerned about efficiency in Scooch as it is not runtime.
            if func_name in self._vars:
                return self._vars[func_name]
            try:
                func = self._VAR_FUNCS[func_name]
            except KeyError:
                raise KeyError('No appropriate function "{}" defined in Scooch'.format(func_name))
            value = func(heirarchy, term, value)
        return value

    def _evaluate_vars(self, parent):
        """
        Performs a depth-first search through the dictionary heirarchy to
        find all macro functions and evaluate them, replacing the macros
        with the resulting values.
        Note that in a single string variable macros will be evaluated in 
        the order they occur in the string, so if one macro replaces the entire
        variable, or overwrites other macros, they will not be evaluated.

        Args:
            parent: dict - The current top level dictionary to recurse through
            and evaluate macros.
        """
        for child_key, child_var in parent.items():

            # Recurse for all children that are dictionaries
            if type(child_var) is dict and child_key is not 'PARENT':
                parent[child_key]['PARENT'] = parent
                self._evaluate_vars(parent[child_key])

            # If it is a list of values, treat it like each element in the list has the same
            # key and parent.
            elif type(child_var) is list and child_key is not 'PARENT':
                for idx, sub_var in enumerate(child_var):
                    if type(sub_var) is dict:
                        sub_var['PARENT'] = parent
                        self._evaluate_vars(sub_var)
                    elif type(sub_var) is str:
                        child_var[idx] = self._evaluate_macro(parent, child_key, sub_var)

            # If it is a string evaluate functions for all macros
            elif type(child_var) is str:
                parent[child_key] = self._evaluate_macro(parent, child_key, child_var)

        # Remove the reverse linkages to parents on the way out
        if 'PARENT' in parent.keys():
            del parent['PARENT']

    def save(self, config_file):
        """
        Saves a the configuration fields in yaml format to disk.

        Args:
            config_file: str or file - A file like object or filename describing a yaml file to save
            this class's configuration to.
        """
        if type(config_file) is str:
            with open(config_file, 'w') as f:
                f.write(yaml.safe_dump({k: v for k, v in self.items()}, default_flow_style=False))
        else:
            config_file.write(yaml.safe_dump({k: v for k, v in self.items()}, default_flow_style=False))
            
    @property
    def json(self):
        """
        Returns a string containing a json version of the dictionary that is unique for a unique configuration,
        and identical for identical configurations.

        Return:
            str - A json formatted string describing the dictionary contents
        """
        return json.dumps(self, sort_keys=True)

    @property
    def hashid(self):
        """
        Returns an identifier that will be the same for identical dictionary contents.
        Note there may be a hash collision here for two distinct contents, but it is very unlikely.

        Return:
            str - A string containing a hex representation of the hashed dictionary.
        """
        return hashlib.sha256(self.json.encode()).hexdigest()
