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
    'pyyaml==5.4.1',
    'sphinx<3.0',
    'sphinx_rtd_theme==0.5.1',
    'ruamel.yaml==0.16.12',
    'click==8.0.0a1'
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
    version='0.0.4',
    description='A python module for configuring hierarchical class structures in yaml with defaults',
    install_requires=REQUIRED_PACKAGES,
    python_requires='>=3.5',
    packages=setuptools.find_packages(),

    # CLI
    entry_points = {
        'console_scripts': ['configipy=configipy.cli:main']
    }
)
