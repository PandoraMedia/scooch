.. _benefits:

Benefits of Scooch
--------------------------------

Many python configuration libraries can help the type of iterative workflows practiced in machine learning, by centralizing the configuration of your iterations to a configuration file. However, because Scooch is object oriented, there are a number of benefits that we believe make it a particularly good choice.

Plug and play code configuration
`````````````````````````````````

Because the config file corresponds directly to the types in a class hierarchy, the selection of subclasses in that code can be configured right there in the config file. This is useful when you implement several different methodologies for doing a single task. For example, an ML practitioner may implement several different ways of augmenting data within a class that creates create mini batches for a gradient descent algorithm. Those "augmenters" may do things like add noise, translate, and rotate the data. That practitioner could write an `Augmenter` base class, and several subclasses `NoiseAugmenter`, `TranslationAugmenter` and `PitchShiftAugmenter`. Each of these subclasses will be selectable and configurable by adjusting the configuration file, without any changes in the code. Furthermore, several configurations of the same class could be created simply by adjusting the config file. This mirrors the benefits of abstraction and polymorphism in OOP. For example, a `Batcher` with many augmenters might be configured like so:

.. code-block:: yaml

    Batcher:
        augmenters:
            - NoiseAugmenter:
                min_noise: 10.0
                max_noise: 20.0
            - NoiseAugmenter:
                min_noise: -10.0
                max_noise: 15.0
            - PitchShiftAugmenter:
                min_shift: 0.0
                max_shift: 10.0
            - TranslationAugmenter:
                displacement_variance: 23
        ...

Each class type of augmenter is implemented in the code once, and the number, types and configurations of the augmenters above can be adjusted without any changes to the code. 

The ability to select and choose functionality in the code by adjusting your config file to describe that functionality by class, and all parameters therein, discourages the use of `case` statements in the code that may switch between functionality via strings / enums (e.g., `alg1`, `alg2`, `alg2.5`, `alg-latest`). The latter can be difficult to maintain and difficult to track as each `case` is an arbitrary string / name that may pertain to a different parameterization mixed with a different code path.

Automatic construction of class hierarchies
````````````````````````````````````````````````````

Because your config file describes the class hierarchy itself, constructing a class hierarchy with a Scooch config file is very simple. The config file provides enough information to construct the class, assign parameters, and furthermore, construct any encapsulated classes within. As we see in the example in the section [How is a Scooch configuration translated into code?](#how-is-a-scooch-configuration-translated-into-code), construction of the class hieararchy is performed in a single line of code, with no adjustments necessary to each of the `Configurable` class's constructors. 

This is difficult to do with other python configuration packages that are not object oriented, in that, they do not construct the configured components, simply translate parameters from config files to variables in code. Furthermore, there may be no standard around how and where the config values are assigned in the code, leading to config files that have a non-intuitive mapping to the code itself. By describing class hierarchies directly in config files, we can avoid class construction boilerplate, and avoid config files that are mapped to code like "sphagetti".

Encourages modular code
``````````````````````````

Because Scooch is fundamentally object oriented, it encourages thinking about code configurations in terms of types and parameters. This practice encourages a developer to think about each of the types and how they interface with both the configuration and any classes that use them, thereby making reusable modules (i.e., classes) and their respective configurations in the code more common, rather than script / purpose specific configurations that may have no interface. After using Scooch for some time, it can become common to write the `config.yaml` file, before implementing the classes it describes, as a way of drafting a class hierarchy's structure.

Namespacing is implicit in your class hierarchies
````````````````````````````````````````````````````

Because the parameters in a configuration file correspond directly to classes and their attributes, there is a 1:1 mapping from namespaces in your configuration file, to class namespaces in the code. The hierarchy in your config file, corresponds directly to the class hierarchy in your code - any parameter within a class in your config file will be assigned to that class in your execution code. This mirrors the benefits of Encapsulation in OOP.

Configuration validation
``````````````````````````

Because Scooch is directly constructing class hierarchies from config files, it knows the expected structure of your class hierarchy, and the types therein. This enables useful error messages that describe the incompatibility between your configuration and the code you are configuring. Given that the config files are human written and human adjusted, this is not uncommon and can improve workflow.

For example, if you specify a configuration for an incorrect Configurable type, e.g.,

.. code-block:: yaml

    Batcher:
        augmenters:
            - NiseAugmenter:
                min_noise: 10.0
                max_noise: 20.0

an error message will be logged like so:

.. code-block:: none

    Provided configuration does not match any, or matches multiple classes in the provided class hierarchy
    Candidates were: ['PitchShiftAugmenter', 'NoiseAugmenter', 'TranslationAugmenter']
    Config requested: ['NiseAugmenter']

If you forget to insert a required parameter, or mispell its name in the configuration file, you will get an error message. For example, if you mispell `min_noise` as `min_nois` for the NoiseAugmenter class, you will get the following error:

.. code-block:: none

    ValueError: Scooch config error: min_noise value not found in NoiseAugmenter object configuration

These error messages can help expedite your debugging process as they catch the configuration errors at the time of construction, rather than at the time of execution.

Hashable configurations
``````````````````````````

Scooch implements functionality to retrieve hashes for configurations, or parts thereof, ensuring that equivalent configurations hash to equivalent identities. This can be useful in ML workflows where logging parameters is important for experiment tracking and reproducability. For example,

1. When logging experiments or features to a database, you may want to index configurations by configuration hash for retrieval by configuration.
2. When running experiments or logging ML features, you may want to compare the experiment or feature's configuration against previously processed examples to prevent duplicate compute and storage.

A CLI for exploring class hierarchies
```````````````````````````````````````

As codebases that use Scooch grow, the number of classes and configuration options can become daunting for on-boarding new users of that codebase. To help with this, Scooch offers some CLI options for exploring configurations, classes and options in a codebase.

If you want to explore all subclass "options" for a given base class, you can use the following command:

.. code-block:: bash

    scooch options -m batcher -f Augmenter

Where the `-m` option specifies a module that the Scooch `Configurable` hierarchy is defined in (must be in your `PYTHONPATH`), and `-f` specifies the `Configurable` type for which you want to view the options for.

If you want to construct a skeleton config file for a given class, you can use the scooch wizard (currently in alpha):

.. code-block:: bash

    scooch construct -c ./config.yaml -f Batcher -m batcher

The wizard will prompt for selecting options for any `Configurable` attributes in the `Batcher` class. Once complete ./config.yaml will be produced, populated by defaults and documentation on each of the parameters.
