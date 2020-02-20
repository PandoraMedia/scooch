.. Congigipy documentation master file, created by
   sphinx-quickstart on Wed Feb 19 22:09:10 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Configipy Documentation
=====================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   config
   configurable

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

About
=====

Configipy allows yaml configs of class hierarchies that are...

 - *Human Readable*
 - *Human Writable*

Human writable in the sense that they are robust to typos and errors,
and human readable in the sense that they don't contain spurious variables
pertaining to the mechanical components of a class, or the data therein, 
only the tunable knobs that humans are interested in.

This functionality is currently implemented in two classes...

 - *Config* - A class for reading in, and performing operations on a human written config
 - *Configurable* - A base class for classes who want to be configurable via config objects

Classes are then configured by yaml config files which provides a sort of user interface
to them.

For the following config file...

.. code-block:: yaml

   Experiment:
      name: test-experiment-${datetime}
      model_cfg:
         DenseNet:
            name: ${inherit}
            num_layers: 3
            layer_width: 1024

It may be used like so....

.. code-block:: python

   from configipy import Config
   
   cfg = Config('./config.yaml') # <= Reads yaml and evaluated macros
   cfg.hashid                    # <= Generates a hash ID unique to this exact configuration
   cfg.json                      # <= Generates a json string for the config
   cfg.Save('./saved_cfg.yaml')  # <= Dumps the config to a yaml files

Given a configurable class hierarchy:

.. code-block:: python

   from configipy import Configurable

   class Model(Configurable):

      _REQUIRED_CONFIG = [
         'name'
      ]
 
      ...

   class DenseNet(Model):

      _REQUIRED_CONFIG = Model._REQUIRED_CONFIG + [
         'num_layers',
         'layer_width'
      ]

      _CONFIG_DEGAULTS = {
         'nonlinearity' = 'relu'
      }

      ...

It may be used like so...

.. code-block:: python

   from configipy import class_instance_for_config

   cfg = Config('./config.yaml')

   # Checks for errors, evaluates default variables
   model = DenseNet(cfg)

   # Classes can be inferred from configs...
   model = class_instance_for_config(Model, cfg['Model']['model_cfg'])

   # Gets the config dictionary the class was constructed with
   model.cfg

   # Instance private variables are automatically populated from Config
   model.num_layers
   
