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


class ConfigCollection(object):
    """
    A Scooch type that may be used to specify the type of sub-configurables a Scooch Configurable has.
    In this case it specifies an arbitrary length list of configurables.
    """

    def __init__(self, subtype):
        """
        **Constructor**

        Args:
            subtype: scooch.Configurable - The type of each Configurable in the dictionary.
        """
        self._subtype = subtype

    @property
    def subtype(self):
        """
        Retrieves the class specifying the type of Scooch Configurable expected in this dictionary.
        """
        return self._subtype
        