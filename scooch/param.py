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
    A Param that is not itself a scooch Configurable. For example, ints, floats, strings, or
    lists and dicts thereof.
    Params that are scooch Configurable class's should be of type ConfigurableParam.
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
        return f"<{str(self._type.__name__)}> - {self._doc}"

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
        return instance._cfg[owner.__name__][self._name]
