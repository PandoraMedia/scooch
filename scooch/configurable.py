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

    __SCOOCH_NAME__ = None
    
    __PARAMS__ = {
        "config_namespace": "<str> - A namespace for the configuration, configs in distinct namespaces will have distinct identities."
    } # <= Parameters that can be specified in the class's configuration

    __CONFIGURABLES__ = {} # <= Parameters that are Scooch configurables and will be constructed according to the configuration dicts specified in the Config

    __PARAM_DEFAULTS__ = {
        "config_namespace": DEFAULT_NAMESPACE
    } # <= Parameters that are optional, and if not provided, will assume default values

    def __init__(self, cfg):
        """
        **Constructor.**

        Args:
            cfg: dict - An object providing the configuration parameters for this object.
        """
        # TODO [matt.c.mccallum 11.04.21]: Gracefully handle the error case that the top-level dictionary is not a single key value corresponding to a class...
        if not cfg[self.__class__.__name__]:
            self._cfg = {self.__class__.__name__: {}}
        else:
            # Save configuration dictionary
            self._cfg = cfg

        required_config = list(self.__PARAMS__.keys())

        # Populate defaults
        self._populate_defaults_recurse(self._cfg[self.__class__.__name__], self.__PARAM_DEFAULTS__)

        # Verify configuration
        # NOTE [matt.c.mccallum 12.16.20]: Just do this for this configurable, all sub-configurables will be verified upon their construction, respectively.
        self._verify_config(self._cfg[self.__class__.__name__], required_config)

        # Construct configurables
        self._config_factory = ConfigurableFactory()
        self._config_instances = {}
        for param_name, configurable in self.__CONFIGURABLES__.items():
            obj = self._config_factory.construct(configurable, self._cfg[self.__class__.__name__][param_name])
            self._config_instances[param_name] = obj

    @classmethod
    def populate_defaults(cls, cfg):
        """
        Populates the defaults for this Configurable in the provided cfg, without actually constructing it.

        Args:
            cfg: Config / Dict - A configuration for this configurable to be populated with defaults where missing
            config values exist.
        """
        cls._populate_defaults_recurse(cfg[cls.__name__], cls.__PARAM_DEFAULTS__)

    @classmethod
    def _populate_defaults_recurse(cls, cfg, defaults):
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
                cls._populate_defaults_recurse(cfg[field], value)

    def _verify_config(self, cfg, template):
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
                        raise ValueError("Scooch config error: " + key + " value not found in " + self.__class__.__name__ + " object configuration")
                    self._verify_config(cfg[key], field[key])
            elif field not in cfg.keys():
                raise ValueError("Scooch config error: " + field + " value not found in " + self.__class__.__name__ + " object configuration")

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
