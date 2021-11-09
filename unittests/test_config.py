"""
Created 02-14-20 by Matt C. McCallum
"""


# Local imports
from configipy import Config
from configs import test_config

# Third party imports
# None.

# Python standard library imports
import unittest
import os


class TestBigtableTable(unittest.TestCase):

    def test_macro_vars(self):
        """
        """
        # TODO [matt.c.mccallum 01.13.20]: Add assert statements here to make this more
        #                                  effective as an automated test.

        cfg = Config(test_config)
        print(cfg) # <= Visually inspect that the macro variables were correctly evaluated.
        
        
if __name__=='__main__':
    unittest.main()
