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
# None.


class ConfigurableParam:
    """
    A scooch parameter that is itself a scooch Configurable object.
    """

    def __init__(self, configurable_type, doc=""):
        """
        **Constructor**

        Args:
            configurable_type: Configurable, ConfigList or ConfigCollection - A scooch configurable type that
            specifies the class hierarchy for which this is a configuration for.

            doc: str - Docs describing what this param does in the context of its encapsulating Configurable
            class.
        """
        # TODO [matt.c.mccallum 11.04.21]: Ensure type is a configurable.
        self._type = configurable_type
        self._doc = doc

    @property
    def type(self):
        return self._type

    @property
    def doc(self):
        return f"<Configurable({str(self._type.__name__)})> - {self._doc}"

    def __set_name__(self, owner, name):
        """
        Assigns the name of the configurable. Any leading underscores are removed.

        Args:
            owner: Configurable - The scooch Configurable class that owns this ConfigurableParam.

            name: str - The name of the ConfigurableParam as an attribute in the owning Configurable.
        """
        self._name = name.lstrip('_')

    def __get__(self, instance, owner):
        """
        Returns the value of the parameter when the ConfigurableParam is accessed as an attribute
        of a Configurable class.

        Args:
            instance: Configurable - The instance of the class that this ConfigurableParam is an 
            attribute of.

            owner: Configurable - The class that this ConfigurableParam is a ConfigurableParam of.
        """
        # TODO [matt.c.mccallum 11.04.21]: Make sure owner is of type Configurable
        return instance._config_instances[self._name]
        