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


DEFAULT_NAMESPACE = "root" # TODO [matt.c.mccallum 11.04.21]: <= Should be private

from enum import Enum
class ParamDefaults(Enum):
    NO_DEFAULT = 0

from .config import *
from .configurable import *
from .config_list import *
from .config_collection import *
from .config_factory import *
from .param import Param
from .configurable_factory import ConfigurableFactory

# TODO [matt.c.mccallum 01.05.21]: Remove the two below in favor of the config factory, once legacy codebases are updated.
from .configurize_helper import configurize
