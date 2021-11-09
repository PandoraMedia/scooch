.. _benefits:

Why Object Oriented Configs?
--------------------------------

Many python configuration libraries can help the type of iterative workflows practiced in machine learning, by centralizing the configuration of your iterations to a configuration file. However, because Scooch is object oriented, there are a number of benefits that we believe make it a particularly good choice.

Plug and play code configuration
`````````````````````````````````

Because the config file corresponds directly to the types in a class hierarchy, the selection of subclasses in that code can be configured right there in the config file. This is useful when you implement several different methodologies for doing a single task. 

For example, an ML practitioner may implement several different ways of augmenting data within a class that creates create mini batches for a gradient descent algorithm. Those "augmenters" may do things like add noise, translate, and rotate the data. That practitioner could write an :code:`Augmenter` base class, and several subclasses :code:`NoiseAugmenter`\ , :code:`TranslationAugmenter` and :code:`PitchShiftAugmenter`\ . Each of these subclasses will be selectable and configurable by adjusting the configuration file, without any changes in the code. 

Furthermore, several configurations of the same class could be created simply by adjusting the config file. This mirrors the benefits of abstraction and polymorphism in OOP. For example, a :code:`Batcher` with many augmenters might be configured like so:

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

The ability to select and choose functionality in the code by adjusting your config file to describe that functionality by class, and all parameters therein, discourages the use of :code:`case` statements in the code that may switch between functionality via strings / enums (e.g., :code:`alg1`\ , :code:`alg2`\ , :code:`alg2.5`\ , :code:`alg-latest`\ ). The latter can be difficult to maintain and difficult to track as each :code:`case` is an arbitrary string / name that may pertain to a different parameterization mixed with a different code path.

Automatic construction of class hierarchies
````````````````````````````````````````````````````

Because your config file describes the class hierarchy itself, constructing a class hierarchy with a Scooch config file is very simple. The config file provides enough information to construct the class, assign parameters, and furthermore, construct any encapsulated classes within. As we see in the examples on the :ref:`home` homepage, construction of the class hieararchy is performed in a single line of code, with no adjustments necessary to each of the :code:`Configurable` class's constructors. 

This is difficult to do with other python configuration packages that are not object oriented, in that, they do not construct the configured components, simply translate parameters from config files to variables in code. Furthermore, there may be no standard around how and where the config values are assigned in the code, leading to config files that have a non-intuitive mapping to the code itself. By describing class hierarchies directly in config files, we can avoid class construction boilerplate, and avoid config files that are mapped to code like "sphagetti".

Encourages modular code
``````````````````````````

Because Scooch is fundamentally object oriented, it encourages thinking about code configurations in terms of types and parameters. This practice encourages a developer to think about each of the :code:`Configurable` types and how they interface with both the configuration and any classes that use them, thereby making reusable modules (i.e., classes) and their respective configurations in the code more common, rather than script / purpose specific configurations that may have no interface. After using Scooch for some time, it can become common to write the :code:`config.yaml` file, before implementing the classes it describes, as a way of drafting a class hierarchy's structure.

Simplifies code reuse
``````````````````````````

Often in ML pipelines you will want to reuse functionality (and hence configuration) in different tasks throughout the pipeline. For example, you may want to create a feature transformation with a given configuration, that is used to produce batches of data for training an ML model. Then you may want to reuse that transformation to provide inputs to a model during inference. By defining this feature transformation as a Scooch configurable class, we can reuse not only the class, but the Scooch configuration in both tasks. For example, both a :code:`BatcherTask` and a :code:`InferenceTask` may have a configurable :code:`FeatureTransform`:

.. code-block:: python 

    from features import FeatureTransform
    from batcher import Batcher
    from scooch import Configurable
    from scooch import ConfigurableParam

    class Task(Configurable):
        """
        Defines an interface for a task executor to execute tasks with.
        """
        ...

    class BatcherTask(Task):
        """
        Batches data.
        """

        _feature = ConfigurableParam(FeatureTransform, doc="Transforms features for neural net input")
        _batcher = ConfigurableParam(Batcher, doc="Batches feature Data")
        ...

    class InferenceTask(Task):
        """
        Applies inference.
        """

        _feature = ConfigurableParam(FeatureTransform, doc="Transforms features for neural net input")
        _model = ConfigurableParam(Model, doc="A trained model for analyzing features")
        ...

Both classes reuse the same :code:`FeatureTransform` interface, and in the Scooch :code:`config.yaml` file, we can reuse the same configuration:

.. code-block:: yaml

    constants:
        input_feature:
            MelSpectrogramFeature:
                n_bins: 128
                hop_size: 512

    TaskExecutor:
        - BatcherTask:
            feature: ${input_feature}
            batcher: 
                ...
        - TrainTask:
                ...
        - InferenceTask:
            feature: ${input_feature}
            model:
                ...

Namespacing is implicit in your class hierarchies
````````````````````````````````````````````````````

Because the parameters in a configuration file correspond directly to classes and their attributes, there is a 1:1 mapping from namespaces in your configuration file, to class namespaces in the code. The hierarchy in your config file, corresponds directly to the class hierarchy in your code - any parameter within a class in your config file will be assigned to that class in your execution code. This mirrors the benefits of Encapsulation in OOP.

Configuration validation
``````````````````````````

Because Scooch is directly constructing class hierarchies from config files, it knows the expected structure of your class hierarchy, and the types therein. This enables useful error messages that describe the incompatibility between your configuration and the code you are configuring. Given that the config files are human written and human adjusted, this is not uncommon, and can improve workflow.

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

If you forget to insert a required parameter, or mispell its name in the configuration file, you will get an error message. For example, if you mispell :code:`min_noise` as :code:`min_nois` for the :code:`NoiseAugmenter` class, you will get the following error:

.. code-block:: none

    ValueError: Scooch config error: min_noise value not found in NoiseAugmenter object configuration

These error messages can help expedite your debugging process as they catch the configuration errors at the time of construction, rather than at the time of execution.

Hashable configurations
``````````````````````````

Scooch implements functionality to retrieve hashes for configurations, or parts thereof, ensuring that equivalent configurations hash to equivalent identities. This can be useful in ML workflows where logging parameters is important for experiment tracking and reproducability. For example,

1. When logging experiments or features to a database, you may want to index configurations by configuration hash for retrieval by configuration.
2. When running experiments or logging ML features, you may want to compare the experiment or feature's configuration against previously processed examples to prevent duplicate compute and storage.

Automatic documentation
```````````````````````

Scooch will automatically append configuration information to each of your classes' doc strings. This can be helpful for understanding a new codebase, auto-generating :code:`sphinx` documentation, etc..

For example, the docstring for a Scooch configurable :code:`Batcher` class might look something like:

.. code-block:: none

    Constructs mini-batches for gradient descent.

    **Scooch Parameters**:

    **config_namespace** (Default: root):
        <str> - A namespace for the configuration, configs in distinct namespaces will have distinct identities.

    **batch_size** (Default: 128):
        <int> - The number of samples in each mini-batch

    **audio_samples_per_smaple** (Default: 1024):
        <int> - The number of audio samples to extract each feature from

    **augmenter** (Configurable: Augmenter):
        <Configurable(Augmenter)> - An augmentation transformation to be applied to each sample


A CLI for exploring class hierarchies
```````````````````````````````````````

As codebases that use Scooch grow, the number of classes and configuration options can become daunting for on-boarding new users to that codebase. To help with this, Scooch offers some CLI options for exploring configurations, classes and options in a codebase.

If you want to explore all subclass "options" for a given base class, you can use the following command:

.. code-block:: bash

    scooch options -m batcher -f Augmenter

Where the :code:`-m` option specifies a module that the Scooch :code:`Configurable` hierarchy is defined in (must be in your :code:`PYTHONPATH`), and :code:`-f` specifies the :code:`Configurable` type for which you want to view the options for.

If you want to construct a skeleton config file for a given class, you can use the Scooch wizard (currently in alpha):

.. code-block:: bash

    scooch construct -c ./config.yaml -f Batcher -m batcher

The wizard will prompt for selecting options for any :code:`Configurable` attributes in the :code:`Batcher` class. Once complete :code:`./config.yaml` will be produced, populated by defaults and documentation on each of the parameters.
