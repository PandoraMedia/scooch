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
# None.

# Local imports
from .configurable_meta import ConfigurableMeta
from .config_list import ConfigList
from .config_collection import ConfigCollection
from .helper_funcs import class_instance_for_config
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
            output_obj = class_instance_for_config(cfg_type, Config(cfg))
        else:
            raise TypeError(f'{self.__class__.__name__} requested to construct class with Configurable parameter of type {str(type(cfg_type))}. Eligible types include ConfigList, ConfigCollection or a subclass of Configurable')
        return output_obj
        
