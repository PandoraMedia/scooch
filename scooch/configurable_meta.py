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
import textwrap
import inspect
from abc import ABCMeta

# Third party imports
# None.

# Local imports
from . import ParamDefaults
from .param import Param
from .config_list import ConfigList
from .config_collection import ConfigCollection


# NOTE [matt.c.mccallum 04.07.22]: ABCMeta is perhaps the most commonly used metaclass in python.
#      We inherit from it in this metaclass to prevent the most common metaclass conflicts with
#      third party libraries
class ConfigurableMeta(ABCMeta):
    """
    Metaclass for scooch configurables. Enables programmatic modification
    to the classes for things like programmatic class documentation.
    """

    def __new__(cls, name, bases, attrs):
        """
        **Preconstructor.**

        Currently does three things:
            - Collects all parameters and parameter defaults through the Configurable inheretence hierarchy
            - Translates scooch configuration dictionaries into scooch parameter types and vice versa
            - Updates the class doc string with information on its scooch parameters
        """
        # Get all base classes that are also ConfigurableMeta types
        meta_bases = [base for base in bases if type(base) is ConfigurableMeta]

        # Collect all params from base classes\
        cls._collect_param_from_bases(meta_bases, attrs, '__PARAMS__')
        cls._collect_param_from_bases(meta_bases, attrs, '__PARAM_DEFAULTS__')
        cls._collect_param_from_bases(meta_bases, attrs, '__CONFIGURABLES__')

        # Populate dictionaries with any scooch Param classes found on the class.
        for attr_name, value in attrs.items():

            if isinstance(value, Param):

                # Populate __PARAMS__
                attrs['__PARAMS__'][attr_name.lstrip('_')] = value.doc
                # Populate __PARAM_DEFAULTS__
                if value.default != ParamDefaults.NO_DEFAULT:
                    attrs['__PARAM_DEFAULTS__'][attr_name.lstrip('_')] = value.default

                if isinstance(value.type, (ConfigurableMeta, ConfigList, ConfigCollection)):
                    # Add to __CONFIGURABLES__
                    attrs['__CONFIGURABLES__'][attr_name.lstrip('_')] = value.type

        # Check that no params have numeric names - this can happen with private variables, e.g., '_0' is a valid variable name in python.
        for attr_name in attrs['__PARAMS__']:
            if attr_name.isnumeric():
                raise ValueError(f"The Configurable class, {cls.__name__}, has a numeric parameter named {attr_name}, which is disallowed")

        # Create Param attributes that don't already exist from the scooch Configurable dictionaries
        for attr_name in attrs['__PARAMS__']:
            if '_'+attr_name not in attrs and attr_name not in attrs:
                if attr_name in attrs['__CONFIGURABLES__']:
                    attrs['_'+attr_name] = Param(
                        attrs['__CONFIGURABLES__'][attr_name], 
                        attrs['__PARAM_DEFAULTS__'].get(attr_name, ParamDefaults.NO_DEFAULT), 
                        attrs['__PARAMS__'][attr_name]
                    )
                else:
                    attrs['_'+attr_name] = Param(
                        None, # NOTE [matt.c.mccallum 09.06.22]: Currently no way to infer type from the older __PARAM__ class dictionaries. We may address this in the future.
                        attrs['__PARAM_DEFAULTS__'].get(attr_name, ParamDefaults.NO_DEFAULT), 
                        attrs['__PARAMS__'][attr_name]
                    )

        # Update the docs
        if not '__doc__' in attrs:
            attrs['__doc__'] = ""
        attrs['__doc__'] = cls._populate_docs(attrs['__doc__'], attrs['__PARAMS__'], attrs['__PARAM_DEFAULTS__'], attrs['__CONFIGURABLES__'])

        # Rename the class if programmatically defined
        if '__SCOOCH_NAME__' in attrs and attrs['__SCOOCH_NAME__'] is not None:
            name = attrs['__SCOOCH_NAME__']

        return super(ConfigurableMeta, cls).__new__(cls, name, bases, attrs)

    @staticmethod
    def _populate_docs(class_doc, params_dict, defaults_dict, configurables_dict):
        """
        Augments the class's doc string with information about the class's Scooch configuration.

        Args:
            class_doc: str - The class's doc string to be extended with Scooch config information.

            params_dict: dict(str, str) - The class's parameter dict, mapping parameter names to 
            parameter docs.

            defaults_dict: dict(str, object) - The class's defaults dict, mapping parameter names 
            to default parameter values

            configurables_dict: dict(str, Configurable) - The class's configurables dict, mapping
            Scooch configurable attributes to Scooch configurable types.

        Returns:
            class_doc: str - The class's doc string with Scooch configuration information appended.
        """

        if len(list(params_dict.keys())):
            class_doc += textwrap.indent(textwrap.dedent("""

            **Scooch Parameters**:
            """), '    ')

        for param, doc in params_dict.items():
            if param in list(configurables_dict.keys()):
                param_cls = configurables_dict[param]
                if inspect.isclass(param_cls):
                    default_info = f" (Configurable: {configurables_dict[param].__name__})"
                else:
                    # TODO [matt.c.mccallum 03.31.21]: Handle the case of ConfigList and ConfigCollection below...
                    default_info = ""
            elif param in list(defaults_dict.keys()):
                param_value = defaults_dict[param]
                if '\n' in str(param_value) or len(str(param_value)) > 40:
                    param_value = f" (Default is of type {type(param_value)})"
                else:
                    default_info = f" (Default: {defaults_dict[param]})"
            else:
                default_info = ""
            class_doc += textwrap.indent(textwrap.dedent(f"""
                                                **{param}**{default_info}:
                                                    {textwrap.fill(doc, 400)}
                                                """), '    ')

        return class_doc

    @staticmethod
    def _collect_param_from_bases(meta_bases, attrs, param_name):
        """
        Collects a parameter from the attributes of all the provided base classes.

        Args:
            meta_bases: list(Configurable) - A list of base classes from which to collect the parameters.
            This is to be provided in order of inheritance.

            attrs: dict - A dictionary of all attributes for this class that inherits the provided bases.

            param_name: str - The name of the parameter to collect across all provided base classes.
        """
        # Reverse list here to respect the python method resolution order (MRO) in any comprehension statements.
        meta_bases = meta_bases[::-1]
        # Collect the params.
        params = {k:v for base in meta_bases for k, v in base.__dict__[param_name].items()}
        if param_name in attrs.keys():
            params = {**params, **attrs[param_name]}
        attrs[param_name] = params
