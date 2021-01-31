"""
Created 01-05-21 by Matt C. McCallum
"""


# Local imports
from .configurable_meta import ConfigurableMeta
from .config_list import ConfigList
from .config_collection import ConfigCollection
from .helper_funcs import class_instance_for_config
from .config import Config

# Third party imports
# None.

# Python standard library imports
# None.


class ConfigurableFactory( object ):
    """
    A Factory for constructing configipy configurables for a given configuration.
    """

    def Construct(self, cfg_type, cfg):
        """
        This will construct and return a Configipy configurable of a given cfg_type according to the parameterization
        specified in the cfg.

        Args:
            cfg_type: ConfigCollection, ConfigList or ConfigurableMeta class: This specifies the type to construct each
            configipy configurable as.

            cfg: configipy.Config: The config specifying the Configurable's parameterization.

        Return:
            configipy.Configurable (or list or dictionary thereof): The constructed configipy Configurable.
        """
        # TODO [matt.c.mccallum 01.05.21]: TYPE CHECK THAT THE CONFIG LISTS AND DICTS MATCH UP WITH THE `cfg_type` HERE.
        if isinstance(cfg_type, ConfigCollection):
            output_obj = {name: self.Construct(cfg_type.subtype, cfg) for name, cfg in cfg.items()}
        elif isinstance(cfg_type, ConfigList):
            output_obj = [self.Construct(cfg_type.subtype, each_cfg) for each_cfg in cfg]
        elif type(cfg_type) is ConfigurableMeta:
            # TODO [matt.c.mccallum 01.13.21]: Move the below method to a member function once we have updated all other codebases to use the ConfigurableFactory instead.
            output_obj = class_instance_for_config(cfg_type, Config(cfg))
        else:
            raise TypeError(f'{self.__class__.__name__} requested to construct class with Configurable parameter of type {str(type(cfg_type))}. Eligible types include ConfigList, ConfigCollection or a subclass of Configurable')
        return output_obj
        
