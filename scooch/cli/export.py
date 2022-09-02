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
# None

# Third party imports
# None

# Local imports
from ..generic import nest_keys
from ..generic import merge_dicts
import yaml


def _parse_param(param):
    """
    Parses a command line parameter into a single element parameter dictionary.

    Args:
        param: str - A string equating the path to the value to the value itself. 
        The value is expected to be yaml formatted.

    Return:
        dict() - A dictionary that is the depth of the path in the provided param
        string, containing the value in that string.
    """
    # TODO [matt.c.mccallum 09.01.22]: Any additional sanitization, e.g., ensuring alphanumeric dictionary keys.
    keys = param.split('=', 1)[0].split('.')
    value = param.split('=', 1)[1]
    return yaml.load('{' + ': {'.join(keys) + ': ' + value + '}'*len(keys), Loader=yaml.FullLoader)


def parse_custom_params(custom_params_list):
    """
    Turns a list of strings formatted like so:

        ['path.to.value=value', ...]

    into a configuration dictionary containing each and all of the specified paths to values.

    Args:
        custom_params_list: <list(str)> - A list of strings specifying custom parameters.

    Return:
        <dict> - A dictionary containing only the specified custom parameters.
    """
    custom_param_dicts = [_parse_param(param) for param in custom_params_list]

    print(custom_param_dicts)
    # Check for duplicate paths

    # custom_param_dicts = [nest_keys(mapping) for mapping in params_to_values]
    seed_dict = {}
    while len(custom_param_dicts):
        seed_dict = dict(merge_dicts(seed_dict, custom_param_dicts[0]))
        del custom_param_dicts[0]
    return seed_dict
