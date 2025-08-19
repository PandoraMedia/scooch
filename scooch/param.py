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
from . import ParamDefaults


class Param:
    """
    A Param that is an attribute of a Configurable, this can be a simple type, or a Configurable type itself. 
    For example, simple types include ints, floats, strings, or lists and dicts thereof, and Configurable types
    are any class that inherits from Configurable.
    """

    def __init__(self, param_type, default=ParamDefaults.NO_DEFAULT, doc=""):
        """
        **Constructor**

        Args:
            param_type: object - The type of this parameter.

            default: object - The value of this Param, if it is not set in the scooch Config. This argument
            defaults to ParamDefaults.NO_DEFAULT, which will result in an error if the Param is missing from
            the scooch Config.

            doc: str - Docs describing what this param does in the context of its encapsulating Configurable
            class.
        """
        self._doc = doc
        self._type = param_type
        self._default = default

    @property
    def default(self):
        return self._default

    @property
    def doc(self):
        return self._doc

    @property
    def type(self):
        return self._type

    def __set_name__(self, owner, name):
        """
        Assigns the name of the configurable. Any leading underscores are removed.

        Args:
            owner: Configurable - The scooch Configurable class that owns this Param.

            name: str - The name of this Param as an attribute in the owning Configurable.
        """
        self._name = name.lstrip('_')
    
    def __get__(self, instance, owner):
        """
        Returns the value of the parameter when the Param is accessed as an attribute
        of a Configurable class.

        Args:
            instance: Configurable - The instance of the class that this Param is an 
            attribute of.

            owner: Configurable - The class that this Param is a Param of.
        """
        # TODO [matt.c.mccallum 11.04.21]: Make sure owner is of type Configurable

        # If called on the class (i.e., no instance), then return the parameter itself
        if instance is None:
            return self
        # Otherwise return the value
        return instance._config_instances[self._name]

    def __set__(self, instance, value):
        """
        Sets the value of a parameter, keeping this separated from the object's config that
        was provided upon construction.

        Args:
            instance: Configurable - The instance to change the value of a config item for.

            value: object - The value to change the config item to.
        """
        # If alias, raise error.
        if self._name in instance.__PARAM_ALIASES__:
            raise ValueError(f"Attempted to change the value of the '{self._name}' parameter, which is an alias and is not settable.")
        # If configurable, gotta construct it populate defaults.
        if self._name in instance.__CONFIGURABLES__:
            if isinstance(value, (dict,)):
                obj = instance._config_factory.construct(instance.__CONFIGURABLES__[self._name], value)
            elif not isinstance(value, (Configurable, None)):
                raise ValueError(f"Attempted to set parameter of type Configurable with object other than (dict, Config, Configurable or None)")
            instance._config_instances[self._name] = obj
        else:
            # TODO [mmccallum 05.07.24]: Add type checking here.
            instance._config_instances[self._name] = value    

        # Update config dictionary:
        instance._cfg[instance.__class__.__name__][self._name] = value

        # Update aliases:
        instance.update_aliases()
