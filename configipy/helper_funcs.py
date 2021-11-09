"""
Created 10-16-19 by Matt C. McCallum
"""


# Local imports
# None

# Third party imports
# None.

# Python standard library imports
# None.


def _all_subclasses(cls):
    """
    cls.__subclasses__ only transcends one level of inheretance so this is a simple 
    recursion to find all subclasses.

    Args:
        cls: object - The class to find all subclasses for.
    """
    return list(set(cls.__subclasses__()).union([s for c in cls.__subclasses__() for s in _all_subclasses(c)]))


def class_for_config(base_class, config):
    """
    Returns the feature class for a given config dictionary or Configipy Config object.
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
    fclsses = _all_subclasses(base_class)
    feature_class_names = [clsobj.__name__ for clsobj in fclsses]

    # Search for matching configuration
    config_fields = config.keys()
    matching_classes = [c_field for c_field in config_fields if c_field in feature_class_names]
    if not len(matching_classes):
        print(feature_class_names)
        print(config_fields)
        raise KeyError('Provided configuration does not match any, or matches multiple classes in the provided module')

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
    