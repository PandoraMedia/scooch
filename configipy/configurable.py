"""
Created 06-17-18 by Matt C. McCallum
"""


# Python standard library imports
import copy

# Third party module imports
# None

# Local imports
from . import DEFAULT_NAMESPACE
from .configurable_meta import ConfigurableMeta
from .configurable_factory import ConfigurableFactory


class Configurable(object, metaclass=ConfigurableMeta):
    """
    A Base class for any object that has a given configuration, i.e., requires a certain set of parameters.

    The configuration may include a heirarchy. That is, in the list of required fields may be a dictionary
    with each key corresponding to a name of a sublist of feilds and each key being a list corresponding to 
    that sublist of field names.

    Note that anything below the top level of the heirarchy will not be assigned as an attribute.
    It is assumed that values further down the heirarchy are for configuration of other objects and it is
    up to the derived class to use these values.
    """
    
    __PARAMS__ = {
        "config_namespace": "<str> - A namespace for the configuration, allowing grouping of configurations, or two configurations with otherwise identical configurations to be distinct."
    } # <= Parameters that must be specified in the class configuration

    __CONFIGURABLES__ = {} # <= Parameters that at Configipy configurables and will be constructed according to the configuration dicts specified in the Config

    __PARAM_DEFAULTS__ = {
        "config_namespace": DEFAULT_NAMESPACE
    } # <= Parameters that are optional, and if not provided, will assume default values

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
        self._config_factory = ConfigurableFactory()
        for param_name, configurable in self.__CONFIGURABLES__.items():
            obj = self._config_factory.Construct(configurable, self._cfg[self.__class__.__name__][param_name])
            setattr(self, "_"+param_name, obj)

    def _populateDefaults(self, cfg, defaults):
        """
        Iterates through all of the items in the defaults and transfers them over to the configuration
        if they are not already there.

        Args:
            cfg: dict() - An object to be used to configure a configurable class

            defaults: dict() - A set of defaults to configure in `cfg` if they do not already exist there.
        """
        # If no config was provided for this class, start with an empty dictionary.
        if cfg is None:
            cfg = dict()
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
        # TODO [matt.c.mccallum 01.05.21]: ADD TYPE CHECKING HERE - CHECK ALL CONFIGURABLES ARE OF THE RIGHT TYPE,
        #      AND THOSE THAT ARE LISTS OF CONFIGURABLES SHOULD BE LISTS ALSO.
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

    @classmethod
    def _all_subclasses(cls):
        """
        cls.__subclasses__ only transcends one level of inheretance so this is a simple 
        recursion to find all subclasses.

        Returns:
            list(Configurable) - A list of all eligible configurables that derive from this class.
        """
        return list(set(cls.__subclasses__()).union([s for c in cls.__subclasses__() for s in c._all_subclasses()]))
