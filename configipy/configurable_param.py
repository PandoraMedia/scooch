"""
Created 11-03-21 by Matt C. McCallum
"""


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
        return self._doc

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
        