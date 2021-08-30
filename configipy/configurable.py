"""
Created 06-17-18 by Matt C. McCallum
"""


# Python standard library imports
import copy
import re
import textwrap

# Third party module imports
from ruamel.yaml.comments import CommentedMap

# Local imports
from configipy.config_list import ConfigList
from .configurable_meta import ConfigurableMeta
from .config_collection import ConfigCollection
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

    @classmethod
    def CreateConfig(cls, interactive, level=0):
        """
        Generates a configuration for this configurable, with all default values filled out,
        comments in place, and sub-configurables selected by the user (or placeholders are
        inserted).

        Args:
            level: int - How many layers deep in a configuration heirarchy we are. This can help with
            printing prompts in interactive mode.

            interactive: bool - Whether to prompt the user to select the types of sub-configurables,
            (true), or to fill them with placeholders.

        Returns: 
            Config - The constructed configurable with placeholders where no defaults exist.
        """
        config = CommentedMap()

        if interactive:
            print(textwrap.indent(f'===\nConfiguring Configurable: {cls.__name__}\n===\n', '  '*level))

        # Add defaults
        config.update(cls.__PARAM_DEFAULTS__)

        def get_subconfig(c_type, docs, level):
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
                return subclss[0].CreateConfig(interactive, level + 1)
            else:
                if interactive:
                    inputting = True
                    while inputting:
                        subcls_names = [f'{idx}: {subcls.__name__}' for idx, subcls in enumerate(subclss)]
                        print(textwrap.indent(f'Select Subclass for Component of Type "{c_type.__name__}":\n-\n{formatted_docs}\n-\n' + '\n'.join(subcls_names), '  '*level + '+ '))
                        try:
                            selection = int(input('  '*level + '+ '))
                            print(' ')
                            inputting = False
                            return subclss[selection].CreateConfig(interactive, level + 1)
                        except (ValueError, IndexError):
                            print(textwrap.indent(f'Invalid value, please enter an integer from 0 to {len(subclss)-1}', '  '*level))
                            print(' ')
                else:
                    return {f'<{c_type.__name__}>': None}

        def unpack_config_collection(c_type, docs, level):
            """
            Configure a collection of sub configurable configurations, optionally with user prompts 
            for types. The collection contains multiple Configurable elements and could be a Collection
            (dict), or a list of n elements.

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
            if isinstance(c_type, ConfigList):
                if interactive:
                    inputting = True
                    while inputting:
                        
                        print(textwrap.indent(f'Choose number of elements in Config List of type "{subtype_name}":\n-\n{formatted_docs}\n-', '  '*level + '+ '))
                        try:
                            number_elem = int(input('  '*level + '+ '))
                            print(' ')
                            inputting = False
                        except ValueError:
                            print(textwrap.indent(f'Invalid value, please enter an integer', '  '*level))
                            print(' ')
                cfg = []
                for _ in range(number_elem):
                    if type(subtype) in (ConfigList, ConfigCollection):
                        cfg += [unpack_config_collection(subtype, docs, level+1)]
                    else:
                        cfg += [get_subconfig(subtype, '', level+1)]
            elif isinstance(c_type, ConfigCollection):
                if interactive:
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
                            if type(subtype) in (ConfigList, ConfigCollection):
                                cfg[name] = unpack_config_collection(subtype, docs, level+1)
                            else:
                                cfg[name] = get_subconfig(subtype, '', level+1)
            return cfg

        # Add configurables
        for param, cfgrble_type in cls.__CONFIGURABLES__.items():
            docs = cls.__PARAMS__[param]
            if type(cfgrble_type) in (ConfigList, ConfigCollection):
                value = unpack_config_collection(cfgrble_type, docs, level+1)
            else:
                value = get_subconfig(cfgrble_type, docs, level+1)
                
            config[param] = value
        
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
