"""
Created 06-17-18 by Matt C. McCallum
"""


# Local imports
from .config_meta import ConfigMeta
from .helper_funcs import class_instance_for_config
from .config import Config

# Third party module imports
# None.

# Python standard library imports
import copy


class Configurable(object, metaclass=ConfigMeta):
    """
    A Base class for any object that has a given configuration, i.e., requires a certain set of parameters.

    The configuration may include a heirarchy. That is, in the list of required fields may be a dictionary
    with each key corresponding to a name of a sublist of feilds and each key being a list corresponding to 
    that sublist of field names.

    Note that anything below the top level of the heirarchy will not be assigned as an attribute.
    It is assumed that values further down the heirarchy are for configuration of other objects and it is
    up to the derived class to use these values.
    """
    
    __PARAMS__ = {} # <= Parameters that must be specified in the class configuration

    __CONFIGURABLES__ = {} # <= Parameters that at Configipy configurables and will be constructed according to the configuration dicts specified in the Config

    __PARAM_DEFAULTS__ = {} # <= Parameters that are optional, and if not provided, will assume default values

    def __init__(self, cfg):
        """
        Constructor.

        Args:
            cfg: dict - An object providing the configuration parameters for this object.
        """
        if not cfg[self.__class__.__name__]:
            self._cfg = {self.__class__.__name__: {}}
        else:
            # Save configuration dictionary
            self._cfg = cfg

        required_config = list(self.__PARAMS__.keys())

        # Populate defaults
        self._populateDefaults(self._cfg[self.__class__.__name__], self.__PARAM_DEFAULTS__)

        # Verify configuration
        # NOTE [matt.c.mccallum 12.16.20]: Just do this for this configurable, all sub-configurables will be verified upon their construction, respectively.
        self._verifyConfig(self._cfg[self.__class__.__name__], required_config)

        # Set properties
        param_config = [it for it in self.__PARAMS__.keys() if it not in list(self.__CONFIGURABLES__.keys())]
        for name in param_config:
            if type(name) is str:
                setattr(self, "_"+name, self._cfg[self.__class__.__name__][name])

        # Construct configurables
        for param_name, configurable in self.__CONFIGURABLES__.items():
            cfg = Config(self._cfg[self.__class__.__name__][param_name])
            setattr(self, "_"+param_name+"_cfg", cfg)
            setattr(self, "_"+param_name, class_instance_for_config(configurable, cfg))

    def _populateDefaults(self, cfg, defaults):
        """
        Iterates through all of the items in the defaults and transfers them over to the configuration
        if they are not already there.

        Args:
            cfg: dict() - An object to be used to configure a configurable class

            defaults: dict() - A set of defaults to configure in `cfg` if they do not already exist there.
        """
        for field, value in defaults.items():
            if field not in cfg.keys():
                cfg[field] = value
            elif isinstance(value, dict):
                # Check the sub fields
                self._populateDefaults(cfg[field], value)

    def _verifyConfig(self, cfg, template):
        """
        Checks that all the required fields in the object configuration are there.

        Args:
            cfg: dict() - An object providing the configuration parameters for this object.

            template: list() - A list of keys that describe the required fields to be configured for this object.
            This may includ dictionaries, allowing a heirarchy in the provided configuration.
        """
        for field in template:
            if isinstance(field, dict):
                for key in field.keys():
                    if key not in cfg.keys():
                        raise ValueError("Configipy config error: " + key + " value not found in " + self.__class__.__name__ + " object configuration")
                    self._verifyConfig(cfg[key], field[key])
            elif field not in cfg.keys():
                raise ValueError("Configipy config error: " + field + " value not found in " + self.__class__.__name__ + " object configuration")

    @property
    def cfg(self):
        """
        Getter function for a copy of this objects configuration.

        Return:
            dict{str:value} : A hierarchical dictionary of this class's configuration and all classes therein.
        """
        return copy.copy(self._cfg)
