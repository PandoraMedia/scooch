# coding=utf-8
# Copyright 2023 Pandora Media, LLC.
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
from .param import Param


class AliasParam(Param):
    """
    A parameter that is deterministically derived from other parameters.
    """

    def __init__(self, param_type, source_param_names, transform_function, doc=None):
        """
        ** Constructor **

        Args:
            param_type: type - The type of the derived parameter.

            source_param_names: list(str) - A list of the names of parameters that this parameter is
            derived from / is an alias for.

            transform_function: func - A function that takes in the parameters defined in 
            source_param_names, and produces the value of this parameter (an alias of the former).

            doc: str - A doc string describing this parameter. If set to None, a string describing
            which parameters this parameter is an alias for will be automatically produced.
        """
        self._type = param_type
        self._transform_function = transform_function
        self._source_param_names = source_param_names

        self._doc = doc
        if doc is None:
            self._doc = f"An alias for the transformation: {self._transform_function.__name__}, \
                          applied to the parameters {source_param_names} in class \
                          {self.__class__.__name__}"
            
        # TODO [matt.c.mccallum 12.18.23]: Check for circular aliases here.
        # TODO [matt.c.mccallum 12.18.23]: Ensure the output type is not a ConfigurableMeta, 
        #      ConfigList or ConfigCollection.

    @property
    def default(self):
        return ParamDefaults.NO_DEFAULT
    
    def __get__(self, instance, owner):
        """
        Returns the value of the parameter when the Param is accessed as an attribute
        of a Configurable class.

        Args:
            instance: Configurable - The instance of the class that this Param is an 
            attribute of.

            owner: Configurable - The class that this Param is a Param of.

        Return: 
            self.type - The value of the aliased parameter.
        """
        # TODO [matt.c.mccallum 12.18.23]: Make sure owner is of type Configurable and includes the
        #      parameters that this parameter is an alias for.

        # If called on the class (i.e., no instance), then return the parameter itself
        if instance is None:
            return self
        # Otherwise return the value
        param_list = []
        for name in self._source_param_names:
            try:
                arg = getattr(instance, '_'+name)
            except AttributeError: 
                arg = getattr(instance, name)
            param_list += [arg]
        return self._transform_function(*param_list)

    def __set__(self, instance, value):
        """
        Sets the value of the parameter. This is disabled for alias parameters which can only be
        changed by adjusting the parameters that the alias parameter is an alias for.

        Args:
            instance: Configurable - The instance to change the value of a config item for.

            value: object - The value to change the config item to.
        """
        raise AttributeError(f'Attempted to set value of SCOOCH parameter {self.name} on an \
                             instance of {instance.__class__.__name__}. This parameter is an alias \
                             and cannot be set directly.')
    