"""
Created 01-05-21 by Matt C. McCallum
"""


# Local imports
# None.

# Third party imports
# None.

# Python standard library imports
# None.


class ConfigList(object):
    """
    A Configipy type that may be used to specify the type of sub-configurables a Configipy Configurable has.
    In this case it specifies an arbitrary length list of configurables.
    """

    def __init__(self, subtype):
        """
        **Constructor**

        Args:
            subtype: Configipy.Configurable - The type of each Configurable in the list.
        """
        self._subtype = subtype

    @property
    def subtype(self):
        """
        Retrieves the class specifying the type of Configipy Configurable expected in this list.
        """
        return self._subtype