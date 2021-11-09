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
import inspect
import functools

# Third party imports
# None.

# Local imports
from .configurable import Configurable


def configurize(cls=None, base_class=None):
    """
    Takes a class and makes it scooch configurable. This will prepend "Conf" to the class name
    to distinguish it from the class definition. The returned / transformed class will be accessible
    via the name assigned in code, although it must be referred to as "Conf<original_class_name>" in
    scooch config files.

    Args:
        cls: class - A python class that will be made configurable via scooch.

        base_class: class - A python class that the newly minted scooch configurable class will inherit 
        from.

    Returns:
        class - The augmented Configurable class that may be configured via scooch.
    """

    def configurize_impl(cls, base_cls=None):

        # TODO [matt.c.mccallum 11.08.21]: Check the class is not already `Configurable`
        # TODO [matt.c.mccallum 11.08.21]: Check that base_cls is `Configurable`
        # TODO [matt.c.mccallum 11.08.21]: Inherit class documentation too

        if base_cls is None:
            base_cls = Configurable

        class DerivedConfigurable(cls, base_cls):
            """
            """

            __SCOOCH_NAME__ = 'Scooch' + cls.__name__

            # TODO [matt.c.mccallum 11.08.21]: Add type info here
            __PARAMS__ = {param: f'<> - Parameter derived by extending base class: {cls.__name__}' for param in inspect.signature(cls).parameters.keys()}

            __PARAM_DEFAULTS__ = {param: val.default for param, val in inspect.signature(cls).parameters.items() if val.default != val.empty}

            def __init__(self, cfg):
                cls.__init__(self, **(cfg[self.__class__.__name__]))
                Configurable.__init__(self, cfg)

        return DerivedConfigurable

    if base_class is None and cls is None:
        return None
    if base_class is None:
        return configurize_impl(cls)
    elif cls is None:
        return functools.partial(configurize_impl, base_cls=base_class)
    else:
        return configurize_impl(cls, base_class)


