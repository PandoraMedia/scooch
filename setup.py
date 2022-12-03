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


# Local imports
# None.

# Third party imports
# None.

# Python standard library imports
import setuptools
import distutils.cmd


long_description = """
# Scooch

Scooch is a recursive acronym for **S**cooch **C**onfigures **O**bject 
**O**riented **C**lass **H**ierarchies, and that's exactly what this package 
does. It is a configuration package for python codebases that simplifies the 
problem of configuring parameters in python code by translating YAML 
configuration files into object oriented class hierarchies.

# Who needs Scooch?

Scooch is useful for people who need an accessible interface to enable 
tweakability in their code. ML practitioners are a good example. They 
typically write code that is intended to be continuously experimented with and 
adjusted in response to observations from running the code. As such, it is useful 
to abstract these tweakable parameters from the code into a config file, providing 
three major benefits:

 - The config file provides a centralized location for adjustable parameters of 
 interest in the code, improving iteration and workflow.
 - Loading, saving and adjusting the configuration of your code is separated 
 from the many other working variables and data structures that may exist in 
 code.
 - The configuration of any part of the code can be hashed, logged, and indexed, 
 to provide a record of the code configuration at any one time.

# Why use Scooch?

There are many other projects out there that endeavor to translate config files 
into parameters in python code, for example:

 - [Gin](https://github.com/google/gin-config)
 - [Sacred](https://sacred.readthedocs.io/en/stable/index.html)
 - [Hydra](https://hydra.cc/)

However, what makes Scooch different is that it not only translates config 
parameters into variables in your code, but into object oriented class 
hierarchies. This means configurations can benefit from object oriented concepts 
such as Inheretance, Encapsulation, Abstraction and Polymorphism.

For more information about how to use, and why to use Scooch. Please refer to 
the [documentation](http://www.mattcmccallum.com/scooch/docs).
"""


REQUIRED_PACKAGES = [
    'pyyaml==5.4.1',
    'sphinx',
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
    name='scooch',
    version='1.0.1',
    description='A python module for configuring hierarchical class structures in yaml with defaults',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://www.mattcmccallum.com/scooch/docs",
    author="Matt C. McCallum",
    author_email="scooch@mattcmccallum.com",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    project_urls={
        'Documentation': 'http://www.mattcmccallum.com/scooch/docs',
        'Bug Reports': 'https://github.com/PandoraMedia/scooch/issues',
        'Source': 'https://github.com/PandoraMedia/scooch',
    },
    license='Apache 2.0',
    keywords='scooch python configuration machine learning',

    install_requires=REQUIRED_PACKAGES,
    python_requires='>=3.6',
    packages=setuptools.find_packages(),
    include_package_data=True,

    # CLI
    entry_points = {
        'console_scripts': ['scooch=scooch.cli:main']
    }
)
