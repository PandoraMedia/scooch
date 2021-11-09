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
import re
import textwrap

# Third party imports
from ruamel.yaml.comments import CommentedMap

# Local imports
from .config_list import ConfigList
from .config_collection import ConfigCollection


class ConfigFactory(object):
    """
    A class for making configurations for class hierarchies out of the box.
    """

    def __init__(self, interactive) -> None:
        """
        **Constructor**

        Args:
            interactive: bool - Whether to prompt user for input when constructing a configuration.
        """
        super().__init__()
        self._interactive = interactive

    def create_config(self, cls, level=0):
        """
        Generates a configuration for this configurable, with all default values filled out,
        comments in place, and sub-configurables selected by the user (or placeholders are
        inserted).

        Args:
            cls: Configurable - A Configurable class to construct a configuration for.

            level: int - How many layers deep in a configuration heirarchy we are. This can help with
            printing prompts in interactive mode.

        Returns: 
            Config - The constructed configurable with placeholders where no defaults exist.
        """
        config = CommentedMap()

        if self._interactive:
            print(textwrap.indent(f'===\nConfiguring Configurable: {cls.__name__}\n===\n', '  '*level))

        # Add defaults
        config.update(cls.__PARAM_DEFAULTS__)

        # Add configurables
        for param, cfgrble_type in cls.__CONFIGURABLES__.items():
            docs = cls.__PARAMS__[param]
            config[param] = self._populate_config(cfgrble_type, docs, level+1)
        
        # Add required parameters and comments
        for ky, val in cls.__PARAMS__.items():
            if ky not in config.keys():
                if re.match("\<([^>]+)\>", val):
                    typestr = re.match("\<([^>]+)\>", val).group(1)
                    config[ky] = f'<{typestr}>'
                else:
                    config[ky] = '<Unspecified Type>'
            config.yaml_add_eol_comment('<= '+val, ky, 65)

        return {cls.__name__: config}

    def _get_subconfig(self, c_type, docs, level):
        """
        Configure a sub configurable configuration, optionally with user prompts for types.

        Args:
            c_type: Configurable - The Configurable to have a configuration constructed for.

            docs: str - The docs to print out in user prompts to explain the config purpose to
            the user.

            level: int - How many layers deep in a configuration heirarchy we are. This can 
            help with printing prompts in interactive mode.
            
        Returns:
            dict - A dictionary containing the constructed configuration
        """
        formatted_docs = textwrap.indent('\n'.join(textwrap.wrap(docs, 80)), '  ')

        subclss = c_type._all_subclasses()
        if len(subclss) == 1:
            return self.create_config(subclss[0], level + 1)
        else:
            if self._interactive:
                inputting = True
                while inputting:
                    subcls_names = [f'{idx}: {subcls.__name__}' for idx, subcls in enumerate(subclss)]
                    print(textwrap.indent(f'Select Subclass for Component of Type "{c_type.__name__}":\n-\n{formatted_docs}\n-\n' + '\n'.join(subcls_names), '  '*level + '+ '))
                    try:
                        selection = int(input('  '*level + '+ '))
                        if selection < 0: raise IndexError  # Prevent negative indexing in UI.
                        print(' ')
                        inputting = False
                        return self.create_config(subclss[selection], level + 1)
                    except (ValueError, IndexError):
                        print(textwrap.indent(f'Invalid value, please enter an integer from 0 to {len(subclss)-1}', '  '*level))
                        print(' ')
            else:
                return {f'<{c_type.__name__}>': None}

    def _unpack_config_list(self, c_type, docs, level):
        """
        Configure a list of sub configurable configurations, optionally with user prompts 
        for types.

        Args:
            c_type: Configurable - The Configurable to have a configuration constructed for.

            docs: str - The docs to print out in user prompts to explain the config purpose to
            the user.

            level: int - How many layers deep in a configuration heirarchy we are. This can 
            help with printing prompts in interactive mode.

        Returns:
            dict - A dictionary containing the constructed configuration
        """
        formatted_docs = textwrap.indent('\n'.join(textwrap.wrap(docs, 80)), '  ')

        subtype = c_type.subtype
        if type(subtype) in (ConfigList, ConfigCollection):
            subtype_name = subtype.__class__.__name__
        else:
            subtype_name = subtype.__name__

        if self._interactive:
            inputting = True
            while inputting:
                
                print(textwrap.indent(f'Choose number of elements in Config List of type "{subtype_name}":\n-\n{formatted_docs}\n-', '  '*level + '+ '))
                try:
                    number_elem = int(input('  '*level + '+ '))
                    if number_elem < 0: raise ValueError
                    print(' ')
                    inputting = False
                except ValueError:
                    print(textwrap.indent(f'Invalid value, please enter a positive integer', '  '*level))
                    print(' ')
        cfg = []
        for _ in range(number_elem):
            if type(subtype) not in (ConfigList, ConfigCollection):
                docs = ''
            cfg += [self._populate_config(subtype, docs, level+1)]
        return cfg

    def _unpack_config_collection(self, c_type, docs, level):
        """
        Configure a collection of sub configurable configurations, optionally with user prompts 
        for types.

        Args:
            c_type: ConfigCollection - The Configurable Collection to have a configuration constructed for.

            docs: str - The docs to print out in user prompts to explain the config purpose to
            the user.

            level: int - How many layers deep in a configuration heirarchy we are. This can 
            help with printing prompts in interactive mode.

        Returns:
            dict - A dictionary containing the constructed configuration
        """
        formatted_docs = textwrap.indent('\n'.join(textwrap.wrap(docs, 80)), '  ')

        subtype = c_type.subtype
        if type(subtype) in (ConfigList, ConfigCollection):
            subtype_name = subtype.__class__.__name__
        else:
            subtype_name = subtype.__name__

        if self._interactive:
            inputting = True
            cfg = {}
            while inputting:
                print(textwrap.indent(f'Creating a collection of type "{subtype_name}":\n-\n{formatted_docs}\n-', '  '*level + '+ '))
                print(textwrap.indent(f'Choose a name for an element in collection of type "{subtype_name}", \nor press enter to finish generating this collection:', '  '*level + '+ '))
                name = input('  '*level + '+ ')
                print(' ')
                if len(name) == 0 or name.isspace():
                    inputting = False
                else:
                    if type(subtype) not in (ConfigList, ConfigCollection):
                        docs = ''
                    cfg[name] = self._populate_config(subtype, docs, level+1)
        return cfg

    def _populate_config(self, cfgrble_type, docs, lvl):
        """
        A hub function to distribute the configuration construction to the correct handler, based on the type
        of configuration required.

        Args:
            cfgrble_type: (Configurable, ConfigList, or ConfigCollection) - A type of configuration to be constructed.

            docs: str - The docs describing the configuration to be constructed.

            lvl: int - How deep in a configuration heirarchy we are - useful for pretty printing user prompts.
        """
        if type(cfgrble_type) is ConfigList:
            value = self._unpack_config_list(cfgrble_type, docs, lvl)
        elif type(cfgrble_type) is ConfigCollection:
            value = self._unpack_config_collection(cfgrble_type, docs, lvl)
        else:
            value = self._get_subconfig(cfgrble_type, docs, lvl)
        return value
