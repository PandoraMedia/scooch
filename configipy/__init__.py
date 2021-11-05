"""
Created 06-21-18 Matt C. McCallum
"""

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
from .configurable_param import ConfigurableParam

# TODO [matt.c.mccallum 01.05.21]: Remove the two below in favor of the config factory, once legacy codebases are updated.
from .helper_funcs import class_for_config
from .helper_funcs import class_instance_for_config
