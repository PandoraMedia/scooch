"""
Created 03-06-19 by Matt C. McCallum
"""


# Local imports
# None.

# Third party imports
# None.

# Python standard library imports
import setuptools
import distutils.cmd


REQUIRED_PACKAGES = [
    'pyyaml',
    'sphinx',
    'sphinx_rtd_theme'
]

class MakeReqsCommand(distutils.cmd.Command):
  """A custom command to export requirements to a requirements.txt file."""

  description = 'Export requirements to a requirements.txt file.'
  user_options = []

  def initialize_options(self):
    """Set default values for options."""
    pass

  def finalize_options(self):
    """Post-process options."""
    pass

  def run(self):
    """Run command."""
    with open('./requirements.txt', 'w') as f:
        for req in REQUIRED_PACKAGES:
            f.write(req)
            f.write('\n')


setuptools.setup(
    cmdclass={
        'make_reqs': MakeReqsCommand
    },
    name='configipy',
    version='0.0.3',
    description='A python module for configuring hierarchical class structures in yaml with defaults',
    install_requires=REQUIRED_PACKAGES,
    packages=setuptools.find_packages()
)
