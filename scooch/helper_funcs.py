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
import logging
import textwrap

# Third party imports
# None.

# Local imports
# None.


def class_for_config(base_class, config):
    """
    Returns the feature class for a given config dictionary or Scooch Config object.
    This class search is performed under the assumption that each key in the dictionary
    or Config is a class in the pandafeet features module.

    Args:
        base_class: object - The base class for which you want to search for derived 
        classes of.

        config: dict - A dictionary with the keys specifying class names in the pandafeet
        features module.

    Return:
        class - The class that can be constructed with the provided config dictionary.
    """
    fclsses = base_class._all_subclasses() + [base_class]
    feature_class_names = [clsobj.__name__ for clsobj in fclsses]

    # Search for matching configuration
    config_fields = config.keys()
    matching_classes = [c_field for c_field in config_fields if c_field in feature_class_names]
    if not len(matching_classes):
        logging.getLogger().error(textwrap.dedent(f"""
                        Provided configuration does not match any, or matches multiple classes in the provided class hierarchy
                        Candidates were: {str(feature_class_names)}
                        Config requested: {str(list(config_fields))}
                        """))
        raise KeyError("""Scooch configuration does not match any, or matches multiple classes in the provided class hierarchy""")

    # Get all matching classes
    f_classes = [fclsses[feature_class_names.index(match_cls)] for match_cls in matching_classes]

    # Return one class if there is only one
    if len(f_classes) == 1:
        return f_classes[0]

    # Otherwise return the list of classes
    return f_classes

def class_instance_for_config(base_class, config):
    """
    Retrieve an instance of a class, constructed with the given configuration.

    Args:
        base_class: object - The base class for which you want to construct a derived class of.

        config: dict or Config - A configuration object specifying the class name (as the first key),
        and class config variables (as a dict in the first value), that you want to construct the class
        with. 
    
    Return:
        object - The constructed class instance that is a derived class of the base class and has been
        configured with the provided config.
    """
    # TODO [matt.c.mccallum 11.06.19]: Update other codebases to use this function where they can.
    return class_for_config(base_class, config)(config)
    