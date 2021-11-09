"""
Created 06-17-18 by Matt C. McCallum
"""


# Local imports
# None.

# Third party module imports
# None.

# Python standard library imports
import copy


class InvalidConfigError(Exception):
    """
    An error that is raised when the required configuration fields are not provided.
    """
    pass


class Configurable(object):
    """
    A Base class for any object that has a given configuration, i.e., requires a certain set of parameters.

    The configuration may include a heirarchy. That is, in the list of required fields may be a dictionary
    with each key corresponding to a name of a sublist of feilds and each key being a list corresponding to 
    that sublist of field names.

    Note that anything below the top level of the heirarchy will not be assigned as an attribute.
    It is assumed that values further down the heirarchy are for configuration of other objects and it is
    up to the derived class to use these values.
    """
    
    _REQUIRED_CONFIG = []   # <= Parameters that must be specified in the class configuration every time

    _CONFIG_DEFAULTS = {}   # <= Parameters that are optional, and if not provided, will assume default values

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

        # Populate defaults
        self._populateDefaults(self._cfg[self.__class__.__name__], self._CONFIG_DEFAULTS)

        # Verify configuration
        self._verifyConfig(self._cfg[self.__class__.__name__], self._REQUIRED_CONFIG)

        # Set properties
        total_config = self._REQUIRED_CONFIG + list(self._CONFIG_DEFAULTS.keys())
        for name in total_config:
            if type(name) is str:
                setattr(self, "_"+name, self._cfg[self.__class__.__name__][name])

    @classmethod
    def GetSubclasses(cls):
        """
        Get all subclasses for this class and place them in a dictionary for indexing and constructing classes from.

        Return:
            dict - A dictionary mapping class names to classes for all current subclasses of this class.
        """
        all_subclasses = []
        for subclass in cls.__subclasses__():
            all_subclasses.append(subclass)
            all_subclasses.extend(subclass._getSubclassNames())
        return {subcls.__name__: subcls for subcls in all_subclasses}

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
                        print(key + " value not found in " + self.__class__.__name__ + " object configuration")
                        raise InvalidConfigError
                    self._verifyConfig(cfg[key], field[key])
            elif field not in cfg.keys():
                print(field + " value not found in " + self.__class__.__name__ + " object configuration")
                raise InvalidConfigError

    @property
    def cfg(self):
        """
        Getter function for a copy of this objects configuration.

        Return:
            dict{str:value} : A hierarchical dictionary of this class's configuration and all classes therein.
        """
        return copy.copy(self._cfg)
