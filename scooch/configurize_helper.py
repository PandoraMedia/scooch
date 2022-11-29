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


def configurize(cls=None, base_class=None, init_base_on_construction=True):
    """
    Takes a class and makes it scooch configurable. This will prepend "Conf" to the class name
    to distinguish it from the class definition. The returned / transformed class will be accessible
    via the name assigned in code, although it must be referred to as "Conf<original_class_name>" in
    scooch config files.

    Args:
        cls: class - A third-party python class that will be made configurable via scooch.

        base_class: class - A python SCOOCH class that the newly minted scooch configurable class will inherit 
        from.

    Returns:
        class - The augmented Configurable class that may be configured via scooch.
    """

    def configurize_impl(cls, base_cls=None, init_base_on_construction=True):

        # TODO [matt.c.mccallum 11.08.21]: Check the class `cls` is not already `Configurable`
        # TODO [matt.c.mccallum 11.08.21]: Check that `base_cls`` is `Configurable`
        # TODO [matt.c.mccallum 11.08.21]: Inherit class documentation too

        if base_cls is None:
            base_cls = Configurable

        class DerivedConfigurable(base_cls, cls):
            """
            """

            __SCOOCH_NAME__ = 'Scooch' + cls.__name__

            # TODO [matt.c.mccallum 11.08.21]: Add type info here
            _BASE_PARAMS = {param: '<> - Parameter derived by extending base class: {cls.__name__}' for param in inspect.signature(base_cls).parameters.keys()}
            _BASE_PARAM_DEFAULTS = {param: val.default for param, val in inspect.signature(base_cls).parameters.items()}        
            _NAME = base_cls.__name__

            __PARAMS__ = {ky: val for ky, val in _BASE_PARAMS.items() if ky not in ['args', 'kwargs']}
            __PARAM_DEFAULTS__ = {ky: val for ky, val in _BASE_PARAM_DEFAULTS.items() if ky not in ['args', 'kwargs'] and hasattr(val, 'default') and val.default != val.empty}
            
            def __init__(self, cfg=None, *args, **kwargs):
                """
                **Constructor.**

                Args:
                    cfg: Config - The scooch config for the loss, including both base class and custom parameters.

                    args: list(obj) - A list of positional arguments, passthrough to any third-party base class.

                    kwargs: dict(str:obj) - A list of keyword arguments, passthrough to any third-party base class.
                """
                if cfg is None:
                    cfg = {self.__class__.__name__ : None}
                elif cfg[self.__class__.__name__] is not None:
                    kwargs.update({ky: val for ky, val in cfg[self.__class__.__name__].items() if ky in self._BASE_PARAMS})
                self._star_args = args
                self._star_kwargs = kwargs
                if init_base_on_construction:
                    self.initialize_base()
                base_cls.__init__(self, cfg)

            def initialize_base(self):
                """
                Initializes the third-party base class with the provided configuration.
                """
                cls.__init__(self, *self._star_args, **self._star_kwargs)

        return DerivedConfigurable

    if base_class is None and cls is None:
        return None
    if base_class is None:
        return configurize_impl(cls)
    elif cls is None:
        return functools.partial(configurize_impl, base_cls=base_class)
    else:
        return configurize_impl(cls, base_class)


