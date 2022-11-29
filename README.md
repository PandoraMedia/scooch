Scooch
===

**S**cooch **C**onfigures **O**bject **O**riented **C**lass **H**ierarchies for python. 

A good place to start with Scooch is at the documentation found [here](http://mattcmccallum.com/scooch/docs).

Scooch is distributed via pypi, so it may be pip installed:

```
pip install scooch
```

Overview
===

- [What is Scooch?](#what-is-scooch)
- [Who needs Scooch?](#who-needs-scooch)
- [Why use Scooch?](#why-use-scooch)
- [What does a Scooch config look like?](#what-does-a-scooch-config-look-like)
- [How is a Scooch configuration translated into code?](#how-is-a-scooch-configuration-translated-into-code)
    
What is Scooch?
===

Scooch is a recursive acronym for **S**cooch **C**onfigures **O**bject **O**riented **C**lass **H**ierarchies, and that's what this package does. It is a configuration package for python codebases that simplifies the problem of configuring parameters in python code by translating YAML configuration files into object oriented class hierarchies.

Who needs Scooch?
===

Scooch is useful for people who need an accessible interface to enable tweakability in their code. ML practitioners are a good example. They typically write code that is intended to be continuously experimented with and adjusted in response to observations from running the code. As such, it is useful to abstract these tweakable parameters from the code into a config file, providing three major benefits:

 - The config file provides a centralized location for adjustable parameters of 
 interest in the code, improving iteration and workflow.
 - Loading, saving and adjusting the configuration of your code is separated 
 from the many other working variables and data structures that may exist in 
 code.
 - The configuration of any part of the code can be hashed, logged, and indexed, 
 to provide a record of the code configuration at any one time.

Why use Scooch?
===

There are many other projects out there that endeavor to translate config files into parameters in python code, for example:

 - [Gin](https://github.com/google/gin-config)
 - [Sacred](https://sacred.readthedocs.io/en/stable/index.html)
 - [Hydra](https://hydra.cc/)

However, what makes Scooch different is that it not only translates config parameters into variables in your code, but into object oriented class hierarchies. This means configurations can benefit from object oriented concepts such as Inheretance, Encapsulation, Abstraction and Polymorphism.

 The benefits of Scooch are outlined in more detail in the [Why Object Oriented Configs?](http://www.mattcmccallum.com/scooch/docs/benefits_of_scooch.html) section of the [docs](http://www.mattcmccallum.com/scooch/docs).

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

Here each class is defined in camel case above, while configruable parameters of each class are written in lower-case with underscores. 

How is a Scooch configuration translated into code?
===

Each class in this configuration corresponds directly to a scooch `Configurable` class in python code. For example the source code for the configuration above might have the following `Configurable` class definitions in `batcher.py`:

```
from scooch import Configurable
from scooch import Param
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
    _max_noise = Param(float, default=10.0, doc="Maximum amount of noise added per sample, in dB")

    ...

class TranslationAugmenter(Augmenter):

    displacement_variance = Param(int, default=50, doc="Number of elemets to rotationally translate the sample by")

    ...

class Batcher(Configurable):
    
    _batch_size = Param(int, default=256, doc="Number of samples per batch")
    _feature = Param(SpectrogramFeature, doc="The feature to produce samples of")
    _augmenters = Param(ConfigList(Augmenter), doc="A list of data augmenters to sample from")
    
    ...
```

In the above snippet, we can see abstraction, polymorphism, inheritance, and encapsulation employed within the classes, and their scooch parameters. Once configured, within each of the classes above the `Param`s and will become accessible as attributes of the encapsulating `Configurable` class instance. Furthermore the scooch `Param` documentation will be added to the `Configurable` class's doc string for accessibilty in any auto-generated documentation.

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
