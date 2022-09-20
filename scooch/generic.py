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
# None


def merge_lists(list1, override):
    """
    Merges a list of dictionaries with a dictionary mapping indices to dictionaries, to
    merge with each specified index in the first list of dictionaries.
    If the overriding value is not a dictionary mapping indices to values, it will replace
    the entire list.
    
    Args:
        list1: list(dict) - A list of dicitonaries to be merged with.

        override: dict(int: dict) - A dictionary mapping indices to dictionaries to merge
        with corresponding indices in list1.

    Return:
        <list> - The merged list of dictionaries.
    """
    # TODO [matt.c.mccallum 08.31.22]: Test for other iterable types that are not lists, e.g., tuples.
    # TODO [matt.c.mccallum 08.31.22]: When the override consists of a list of dicts and is the same length as list1, merge each dict together.
    if isinstance(override, list):
        return override
    elif isinstance(override, dict) and all(isinstance(k, int) for k in override):
        for idx, value in override.items():
            if idx >= len(list1):
                raise ValueError(f"Merging of SCOOCH lists failed. Requested merge at index {idx} but the list to merge into is of length {len(list1)}.")
            if isinstance(list1[idx], dict) and isinstance(value, dict):
                list1[idx] = dict(merge_dicts(list1[idx], value))
            elif isinstance(list1[idx], list) and isinstance(value, dict):
                list1[idx] = merge_lists(list1[idx], value)
            else:
                list1[idx] = value
        return list1
    else:
        # If the overriding value is not a dictionary or list, we can't merge it, so we replace
        # replace the list with the overriding value and move on.
        return override


def merge_dicts(dict1, override):
    """
    Merges two nested dictionaries, resolving conflicts by overwriting anything in the first argument
    (dict1) with that in the second argument (override).

    Args:
        dict1: <dict> - A dictionary to merge with override.

        override: <dict> - A dictionary to merge with dict1, for any key in both dictionaries, the values
        in this dictionary will be selected to override that in dict1.

    Return:
        <(key, dict)> - Generates tuples of key / value pairs. This is to be used in a generator, e.g.,
        to retrieve a complete merged dictionary:
        
            dict(merge_dicts(dict1, override))
    """
    for k in set(dict1.keys()).union(override.keys()):
        if k in dict1 and k in override:
            if isinstance(dict1[k], dict) and isinstance(override[k], dict):
                yield (k, dict(merge_dicts(dict1[k], override[k])))
            elif isinstance(dict1[k], list):
                yield (k, merge_lists(dict1[k], override[k]))
            else:
                # If one of the values is not a dict or list, you can't continue merging it.
                # Value from second dict overrides one in first and we move on.
                yield (k, override[k])
        elif k in dict1:
            yield (k, dict1[k])
        else:
            yield (k, override[k])
