Scooch
===

**S**cooch **C**onfigures **O**bject **O**riented **C**lass **H**ierarchies for python. 

- [What is Scooch?](#what-is-scooch)
- [Who needs Scooch?](#who-needs-scooch)
- [Why use Scooch?](#why-use-scooch)
- [What does a Scooch config look like?](#what-does-a-scooch-config-look-like)
- [How is a Scooch configuration translated into code?](#how-is-a-scooch-configuration-translated-into-code)
- [Benefits of Scooch](#benefits-of-scooch)
    - [Plug and play code configuration](#plug-and-play-code-configuration)
    - [Automatic construction of class hierarchies](#automatic-construction-of-class-hierarchies)
    - [Encourages modular code](#encourages-modular-code)
    - [Namespacing is implicit in your class hierarchies](#namespacing-is-implicit-in-your-class-hierarchies)
    - [Configuration validation](#configuration-validation)
    - [Hashable configurations](#hashable-configurations)
    - [Scooch has a helpful CLI](#scooch-has-a-helpful-cli)
- [FAQ](#FAQ)
    
What is Scooch?
===

Scooch is a recursive acronym for **S**cooch **C**onfigures **O**bject **O**riented **C**lass **H**ierarchies, and that's exactly what this package does. It is a configuration package for python codebases that simplifies the problem of configuring parameters in python code by translating YAML configuration files into object oriented class hierarchies.

Who needs Scooch?
===

Scooch is useful for people who need a good interface to enable "tweakability" in their code. ML practitioners are a good example. They typically write code that is intended to be continuously experimented with and adjusted in response to observations from running the code. As such, it is useful to abstract these tweakable parameters from the code into a config file, providing two major benefits:

 - The config file provides a centralized location for adjustable parameters of interest in the code, improving iteration and workflow.
 - Loading, saving and adjusting the configuration of your code is separated from the many other working variables and data structures that may exist in code.
 - The configuration of any part of the code can be hashed, logged, and indexed, to provide a record of the code configuration at any one time.

Why use Scooch?
===

There are many other projects out there that endeavor to translate config files into parameters in your code, for example:

 - [Gin](https://github.com/google/gin-config)
 - [Sacred](https://sacred.readthedocs.io/en/stable/index.html)
 - [Hydra](https://hydra.cc/)

However, what makes Scooch different is that it not only translates config parameters into variables in your code, but into object oriented class hierarchies. This means configurations can benefit from object oriented concepts such as Inheretance, Encapsulation, Abstraction and Polymorphism. The benefits of Scooch are outlined in more detail in the [Benefits of Scooch](#Benefits-of-Scooch) subsections below.

What does a Scooch config look like?
===

Scooch config files map parameter configurations directly to python class hierarchies, and so your config file becomes a description of all configurable class's inside your class hierarchy. For example, a class designed to batch samples for training an ML model that uses gradient descent might have a `config.yaml` file that looks something like:

```
Batcher:
    batch_size: 128
    feature:
        SpectrogramFeature:
            hop_size: 128
            n_bins: 256
    augmenters:
        - NoiseAugmenter:
            augmentations_per_sample: 3
            min_noise: -20 
            max_noise: 20 
        - TranslationAugmenter:
            augmentations_per_sample: 5
            displacement_variance: 100
```

Here each class is defined in camel case above, while confgiruable parameters of each class are written in lower-case with underscores. 

How is a Scooch configuration translated into code?
===

Each class in this configuration corresponds directly to a scooch `Configurable` class in python code. For example the source code for the configuration above might have the following `Configurable` class definitions in `batcher.py`:

```
from scooch import Configurable
from scooch import Param
from scooch import ConfigurableParam
from scooch import ConfigList

class SpectrogramFeature(Configurable):

    _hop_size = Param(int, default=128, doc="Number of samples between successive spectrogram frames")
    _n_bins = Param(int, default=1024, doc="Number of frequency bins in the spectrogram")

    ...

class Augmenter(Configurable):

    _augmentations_per_sample = Param(int, default=3, doc="Number of augmented samples produced per input sample")

    ...

class NoiseAugmenter(Augmenter):

    _min_noise = Param(float, default=-10.0, doc="Minimum amount of noise added per sample, in dB")
    _max_noise = Param(flaot, default=10.0, doc="Maximum amount of noise added per sample, in dB")

    ...

class TranslationAugmenter(Augmenter):

    displacement_variance = Param(int, default=50, doc="Number of elemets to rotationally translate the sample by")

    ...

class Batcher(Configurable):
    
    _batch_size = Param(int, default=256, doc="Number of samples per batch")
    _feature = ConfigurableParam(SpectrogramFeature, doc="The feature to produce samples of")
    _augmenters = ConfigurableParam(ConfigList(Augmenter), doc="A list of data augmenters to sample from")
    
    ...
```

In the above snippet, we can see abstraction, polymorphism, inheritance, and encapsulation employed within the classes, and their scooch parameters. Once configured, within each of the classes above the `Param`s and `ConfigurableParam`s will become accessible as attributes of the encapsulating `Configurable` class instance. Furthermore the scooch `Param` / `ConfigurableParam` documentation will be added to the `Configurable` class's doc string for accessibilty in any auto-generated documentation.

With the class definitions and the `config.yaml` file provided above, configuring the Batcher class and running the code in a script could be as simple as:

```
from scooch import Config
from batcher import Batcher

# Construct the object - this is all that is required to configure your class hierarchy.
a_batcher = Batcher(Config('./config.yaml'))

# Configurable values are assigned to class attributes
print(a_batcher._batch_size) # <= prints "128"

# Configurable attributes are constructed and assigned to class attributes
print(a_batcher._feature._n_bins) # <= prints "256"

# Use the class to produce a batch with the configured parameters
samples = a_batcher.get_batch()
```

Several common questions around the OOP style of scooch configuration are answered in the [FAQ](#FAQ) section below.

Benefits of Scooch
===

Many python configuration libraries can help the type of iterative workflows practiced in machine learning, by centralizing the configuration of your iterations to a configuration file. However, because Scooch is object oriented, there are a number of benefits that we believe make it a particularly good choice.

Plug and play code configuration
---

Because the config file corresponds directly to the types in a class hierarchy, the selection of subclasses in that code can be configured right there in the config file. This is useful when you implement several different methodologies for doing a single task. For example, an ML practitioner may implement several different ways of augmenting data within a class that creates create mini batches for a gradient descent algorithm. Those "augmenters" may do things like add noise, translate, and rotate the data. That practitioner could write an `Augmenter` base class, and several subclasses `NoiseAugmenter`, `TranslationAugmenter` and `PitchShiftAugmenter`. Each of these subclasses will be selectable and configurable by adjusting the configuration file, without any changes in the code. Furthermore, several configurations of the same class could be created simply by adjusting the config file. This mirrors the benefits of abstraction and polymorphism in OOP. For example, a `Batcher` with many augmenters might be configured like so:

```
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
        - TranslationAugmenteR:
            displacement_variance: 23
    ...
```

Each class type of augmenter is implemented in the code once, and the number, types and configurations of the augmenters above can be adjusted without any changes to the code. 

The ability to select and choose functionality in the code by adjusting your config file to describe that functionality by class, and all parameters therein, discourages the use of `case` statements in the code that may switch between functionality via strings / enums (e.g., `alg1`, `alg2`, `alg2.5`, `alg-latest`). The latter can be difficult to maintain and difficult to track as each `case` is an arbitrary string / name that may pertain to a different parameterization mixed with a different code path.

Automatic construction of class hierarchies
---

Because your config file describes the class hierarchy itself, constructing a class hierarchy with a Scooch config file is very simple. The config file provides enough information to construct the class, assign parameters, and furthermore, construct any encapsulated classes within. As we see in the example in the section [How is a Scooch configuration translated into code?](#how-is-a-scooch-configuration-translated-into-code), construction of the class hieararchy is performed in a single line of code, with no adjustments necessary to each of the `Configurable` class's constructors. 

This is difficult to do with other python configuration packages that are not object oriented, in that, they do not construct the configured components, simply translate parameters from config files to variables in code. Furthermore, there may be no standard around how and where the config values are assigned in the code, leading to config files that have a non-intuitive mapping to the code itself. By describing class hierarchies directly in config files, we can avoid class construction boilerplate, and config files that are mapped to code like "sphagetti".

Encourages modular code
---

Because Scooch is fundamentally object oriented, it encourages thinking about code configurations in terms of types and parameters. This practice encourages a developer to think about each of the types and how they interface with both the configuration and any classes that use them, thereby making reusable modules (i.e., classes) and their respective configurations in the code more common, rather than script / purpose specific configurations that may have no interface. After using Scooch for some time, it can become common to write the `config.yaml` file, before implementing the classes it describes, as a way of drafting a class hierarchy's structure.

Namespacing is implicit in your class hierarchies
---

Because the parameters in a configuration file correspond directly to classes and their attributes, there is a 1:1 mapping from namespaces in your configuration file, to class namespaces in the code. The hierarchy in your config file, corresponds directly to the class hierarchy in your code - any parameter within a class in your config file will be assigned to that class in your execution code. This mirrors the benefits of Encapsulation in OOP.

Configuration validation
---

Because Scooch is directly constructing class hierarchies from config files, it knows the expected structure of your class hierarchy, and the types therein. This enables useful error messages that describe the incompatibility between your configuration and the code you are configuring. Given that the config files are human written and human adjusted, this is not uncommon and can improve workflow.

For example, if you specify a configuration for an incorrect Configurable type, e.g.,

```
Batcher:
    augmenters:
        - NiseAugmenter:
            min_noise: 10.0
            max_noise: 20.0
```

an error message will be logged like so:

```
Provided configuration does not match any, or matches multiple classes in the provided class hierarchy
Candidates were: ['PitchShiftAugmenter', 'NoiseAugmenter', 'TranslationAugmenter']
Config requested: ['NiseAugmenter']
```

If you forget to insert a required parameter, or mispell its name in the configuration file, you will get an error message. For example, if you mispell `min_noise` as `min_nois` for the NoiseAugmenter class, you will get the following error:

```
ValueError: Scooch config error: min_noise value not found in NoiseAugmenter object configuration
```

These error messages can help expedite your debugging process as they catch the configuration errors at the time of construction, rather than at the time of execution.

Hashable configurations
---

Scooch implements functionality to retrieve hashes for configurations, or parts thereof, ensuring that equivalent configurations hash to equivalent identities. This can be useful in ML workflows where logging parameters is important for experiment tracking and reproducability. For example,

 - When logging experiments or features to a database, you may want to index configurations by configuration hash for retrieval by configuration.
 - When running experiments or logging ML features, you may want to compare the experiment or feature's configuration against previously processed examples to prevent duplicate compute and storage.

Scooch has a helpful CLI
---

As codebases that use Scooch grow, they number of classes and configuration options can become daunting for on-boarding new users of that codebase. To help with this, Scooch offers some CLI options for exploring configurations, classes and options in a codebase.

If you want to explore all subclass "options" for a given base class, you can use the following command:

```
scooch options -m batcher -f Augmenter
```

Where the `-m` option specifies a module that the Scooch `Configurable` hierarchy is defined in (must be in your `PYTHONPATH`), and `-f` specifies the `Configurable` type for which you want to view the options for.

If you want to construct a skeleton config file for a given class, you can use the scooch wizard (currently in alpha):

```
configipy construct -c ./config.yaml -f Batcher -m batcher
```

The wizard will prompt for configurable options in the Batcher class and any `Configurable` attributes therein. Once complete ./config.yaml will be produced, populated by defaults and documentation on each of the parameters.

FAQ
===

*Under Construction*
