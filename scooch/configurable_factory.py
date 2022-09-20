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
import logging
import textwrap

# Third party imports
# None.

# Local imports
from .configurable_meta import ConfigurableMeta
from .config_list import ConfigList
from .config_collection import ConfigCollection
from .config import Config


class ConfigurableFactory( object ):
    """
    A Factory for constructing scooch configurables for a given configuration.
    """

    def construct(self, cfg_type, cfg):
        """
        This will construct and return a Scooch configurable of a given cfg_type according to the parameterization
        specified in the cfg.

        Args:
            cfg_type: ConfigCollection, ConfigList or ConfigurableMeta class: This specifies the type to construct each
            scooch configurable as.

            cfg: scooch.Config: The config specifying the Configurable's parameterization.

        Return:
            scooch.Configurable (or list or dictionary thereof): The constructed scooch Configurable.
        """
        # TODO [matt.c.mccallum 01.05.21]: TYPE CHECK THAT THE CONFIG LISTS AND DICTS MATCH UP WITH THE `cfg_type` HERE.
        # TODO [matt.c.mccallum 11.04.21]: Raise a helpful error if we don't get a config list or config collection in the config dict, when we expect one.
        if isinstance(cfg_type, ConfigCollection):
            output_obj = {name: self.construct(cfg_type.subtype, cfg) for name, cfg in cfg.items()}
        elif isinstance(cfg_type, ConfigList):
            output_obj = [self.construct(cfg_type.subtype, each_cfg) for each_cfg in cfg]
        elif type(cfg_type) is ConfigurableMeta:
            # TODO [matt.c.mccallum 01.13.21]: Move the below method to a member function once we have updated all other codebases to use the ConfigurableFactory instead.
            output_obj = self._class_instance_for_config(cfg_type, Config(cfg))
        else:
            raise TypeError(f'{self.__class__.__name__} requested to construct class with Configurable parameter of type {str(type(cfg_type))}. Eligible types include ConfigList, ConfigCollection or a subclass of Configurable')
        return output_obj
        
    def get_class(self, base_class, config):
        """
        Returns the Configurable class for a given config dictionary or Scooch Config object.

        Args:
            base_class: Configurable - The base class for which you want to search for derived 
            classes of.

            config: Config - A dictionary with a key specifying a SCOOCH Configurable class name.

        Return:
            Configurable.__class__ - The class that can be constructed with the provided config 
            dictionary.
        """

        # If looking for the class of a collection or list, unpack these structures to find the type within
        while isinstance(base_class, (ConfigCollection, ConfigList)):
            base_class = base_class.subtype

        # Get all potential classes
        fclsses = base_class._all_subclasses() + [base_class]
        feature_class_names = [clsobj.__name__ for clsobj in fclsses]

        # Search for matching configuration
        config_fields = config.keys()
        matching_classes = [c_field for c_field in config_fields if c_field in feature_class_names]
        if not len(matching_classes):
            logging.getLogger().error(textwrap.dedent(f"""
                            Provided configuration does not match any class in the provided class hierarchy
                            Candidates were: {str(feature_class_names)}
                            Config requested: {str(list(config_fields))}
                            """))
            raise KeyError("""Scooch configuration does not match any class in the provided class hierarchy""")

        # Get all matching classes
        f_classes = [fclsses[feature_class_names.index(match_cls)] for match_cls in matching_classes]

        # Return one class if there is only one
        if len(f_classes) == 1:
            return f_classes[0]
        else:
            raise KeyError(f"Attempted to retrieve class of type {base_class.__name__}, which matches multiple possible classes: {[cl.__name__ for cl in matching_classes]}")

    def _class_instance_for_config(self, base_class, config):
        """
        Retrieve an instance of a class, constructed with the given configuration.

        Args:
            base_class: Configurable - The base class for which you want to construct a derived class of.

            config: Config - A configuration object specifying the class name (as the first key),
            and class config variables (as a dict in the first value), that you want to construct the class
            with. 
        
        Return:
            Configurable - The constructed class instance that is a derived class of the base class and has been
            configured with the provided config.
        """
        return self.get_class(base_class, config)(config)
