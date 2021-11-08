
Batcher Example
===

This example provides a walkthrough in starting a new Scooch configurable codebase for creating mini-batches to be used in a gradient descent algorithm. It highlights many of the features and benefits of using Scooch.

Starting with a new class hierarchy
===

If you are starting a new project, scooch is an easy way to keep your code structured and configurable as you develop. In this example, we'll create a `Batcher` class that produces mini-batches for gradient descent.

To get started create a python environment and install the required packages in the `requirements.txt` file. If you do not already have this example on your machine, you will also need to clone the repo:

```
git clone https://github.com/PandoraMedia/scooch.git
cd ./scooch/examples/batcher
pip install -r ./requirements.txt
```

The example exists in a completed state, so if you would like to build as you go and follow through this walkthrough step-by-step, you'll need to remove the code in this directory (be sure you're in the correct `./examples/batcher` directory of the scooch codebase):

```
rm ./config.yaml
rm ./batch_it.py
rm -r ./batcher
```

1 - Parameterize a class
---

A core componet of this code will be a configurable `Batcher` class. To make a new scooch configurable class, you can simply inherit from `scooch.Configurable` and define some parameters on that class's definition. For the `Batcher` class, we'll start simple by placing the following class in `./batcher.py`:

```
import random
from scooch import Configurable
from scooch import Param
import numpy as np

class Batcher(Configurable):
    """
    Constructs mini-batches for gradient descent.
    """

    _batch_size = Param(type=int, default=128, doc="The number of samples in each mini-batch")
    _audio_samples_per_smaple = Param(int, default=1024, doc="The number of audio samples to extract each feature from")

    def set_data(self, data):
        # Save a reference to a data array, to sample / batch from
        self._data = data

    def get_batch(self):
        feature_data = []
        while len(feature_data) < self._batch_size:
            start_idx = np.random.randint(0, self._data.shape[0]-self._audio_samples_per_smaple)
            audio_segment = self._data[start_idx:(start_idx+self._audio_samples_per_smaple)]
            feature_data += [audio_segment]
        random.shuffle(feature_data)
        return np.vstack(feature_data[:self._batch_size])
```

This class will extract random samples from the provided test data.

2 - Write a config
---

Now that there is a class to configure, you can write a yaml file that will set its parameters, e.g., for the `Batcher` class above:

```
Batcher:
    batch_size: 8
```

Save this as `./config.yaml` in the current working directory.

Note that we need not configure a parameter if we want to use its default value. In this case we'll use the default for `audio_samples_per_sample`. All parameters without a default value defined, are required to be specified in the config file.

Note that the `batch_size` parameter is private to the batcher class, but no leading underscores are used in the config file. With Scooch classes it is preferred to keep parameters private to each class, and expose them as `@property`s where necessary. However this is not required. For example, the `_batch_size` parameter could equivalently be named `batch_size` if the developer prefers public parameters.

3 - Construct and use the class
---

At this point, it is simple to instantiate the class with the specified configuration file and execute methods on it. For example, a script to pull mini-batches from the `Batcher` class could be as simple as:

```
from batcher import Batcher
from scooch import Config
import argparse
import scipy.io.wavfile
import matplotlib.pyplot as plt

NUM_BATCHES = 3

def main(config, data):

    # Load data
    audio_data = scipy.io.wavfile.read(data)[1]/32767 # <= Normalize 16 bit wav format

    # Batch samples
    batcher_instance = Batcher(Config(config))
    batcher_instance.set_data(audio_data)
    batches = [batcher_instance.get_batch() for _ in range(NUM_BATCHES)]

    # Plot batches for inspection
    fig, axs = plt.subplots(1, NUM_BATCHES, sharey=True)
    for batch_num in range(NUM_BATCHES):
        axs[batch_num].plot(batches[batch_num].T)
        axs[batch_num].set_title(f"Batch {batch_num}")
        
    plt.show()

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Produces a few example mini-batches')
    parser.add_argument("--config", default="./config.yaml", type=str)
    parser.add_argument("--data", default="./data/test_data.wav", type=str)
    kwargs = vars(parser.parse_args())
    processed_kwargs = {key: arg for key, arg in kwargs.items() if arg}
    main(**processed_kwargs)
```

For this example, we'll simply plot the data, though this could easily be extended to do something more useful like dump the data to `.npy` files for training a model.

Save this script as `batch_it.py`, it can then be executed as:

```
python ./batch_it.py --config ./config.yaml --data ./data/test_data.wav
```

There we have it, a script that uses scooch to configure a class for producing mini-batches. This can be done simply with many different python config libraries. Next we'll look into some of the benefits of Scooch's object oriented approach in particular.

4 - Encapsulation
---

One of the primary benefits of scooch is that it constructs not only classes, but entire class hierarchies, with minimal code. Perhaps we want the `Batcher` class above to produce augmentations of the data source it is reading from. 

To get started it might make sense to place our `Batcher` class in a python package. We can do this by organizing our previous files like so in the following directories:

```
./batch_it.py
./config.yaml
./batcher/__init__.py
./batcher/batcher.py
```

and place the following in the `./batcher/__init__.py` file:

```
from .batcher import Batcher
```

For data augmentations we'll like want to parameterize that augmentation itself. Let's create an augmenter class that takes in some feature data and augments it. Put the following in the file `./batcher/augmenters.py`

```
import numpy as np
from scooch import Configurable
from scooch import Param

class NoiseAugmenter(Configurable):
    """
    Takes in audio samples and augments them by adding noise, distributed uniformly on
    a logarithmic scale between the minimum and maximum provided noise values.
    """

    _noise_min = Param(float, default=-10.0, doc="Minimum RMS power of noise to be added to an audio sample (in dB)")
    _noise_max = Param(int, default=10.0, doc="Maximum RMS power of noise to be added to an audio sample (in dB)")

    def augment(self, sample):
        # Produce a random dB value for the noise
        power_db = np.random.rand()*(self._noise_max - self._noise_min) + self._noise_min
        # Convert to linear
        power_linear = 10.0**(power_db/10.0)
        # Synthesize and add the noise to the signal
        noise_data = np.random.normal(scale=power_linear, size=sample.shape)
        return sample + noise_data
```

We can now employ this new `Configurable` inside the `Batcher` class by adding a `ConfigurableParam` in the class definition of `Batcher`, e.g., 

```
import random
from scooch import Configurable
from scooch import Param
import numpy as np
from .augmenters import NoiseAugmenter

class Batcher(Configurable):
    """
    Constructs mini-batches for gradient descent.
    """

    _batch_size = Param(int, default=128, doc="The number of samples in each mini-batch")
    _audio_samples_per_smaple = Param(int, default=1024, doc="The number of audio samples to extract each feature from")
    _augmenter = ConfigurableParam(NoiseAugmenter, doc="An augmentation transformation to be applied to each sample")

...
```

Upon instantiation, this class will be constructed and assigned to the `_augmenter` attribute, so using it is simple. We can adjust the `get_batch` method of `Batcher` to do this:

```
...

    def get_batch(self):
        feature_data = []
        while len(feature_data) < self._batch_size:
            start_idx = np.random.randint(0, self._data.shape[0]-self._audio_samples_per_smaple)
            audio_segment = self._data[start_idx:(start_idx+self._audio_samples_per_smaple)]
            feature_data += [self._augmenter.augment(audio_segment)]
        random.shuffle(feature_data)
        return np.vstack(feature_data[:self._batch_size])

...
```

We can now adjust the `./config.yaml` to configure the new `Configurable` class parameter:

```
Batcher:
    batch_size: 8
    augmenter:
        NoiseAugmenter:
            min_noise: -5.0
            max_noise: 5.0
```

Without any changes to the `./batch_it.py` script, scooch will construct the new class hierarchy based on the parameters and configuration, to produce noise augmented samples. Try running the following again:

```
python ./batch_it.py --config ./config.yaml --data ./data/test_data.wav
```

Here we can see that Scooch has constructed the new class hierarchy based on the updated configuration and produced batches of what are now noisy samples.

5 - Inheritance
---

Scooch configures not only classes, but class hierarchies. As this codebase develops it is likely that there'll be several different types of `Augmenter`s. To support this, let's construct an `Augmenter` base class that `NoiseAugmenter` will inherit from. In this class we might also want to include some functionality that is common to all augmenters, e.g., the number of augmentations performed per input sample. To do this, adjust `./augmenters.py` like so:

```
import numpy as np
from scooch import Configurable
from scooch import Param

class Augmenter(Configurable):
    """
    An abstract augmenter base class for all feature augmentations to derive from.
    """

    _augmentations_per_sample = Param(int, default=3, doc="The number of augmentations returned for each input sample")

    def augment(self, sample):
        return [self._get_augmentation(sample) for _ in range(self._augmentations_per_sample)]

    def _get_augmentation(self, sample):
        raise NotImplementedError(f"The augmenter class {self.__class__.__name__} has no defined method to augment a feature.")


class NoiseAugmenter(Augmenter):
    """
    Takes in audio samples and augments them by adding noise, distributed uniformly on
    a logarithmic scale between the minimum and maximum provided noise values.
    """

    _noise_min = Param(float, default=-10.0, doc="Minimum RMS power of noise to be added to an audio sample (in dB)")
    _noise_max = Param(int, default=10.0, doc="Maximum RMS power of noise to be added to an audio sample (in dB)")

    def _get_augmentation(self, sample):
        # Produce a random dB value for the noise
        ...
```

We now adjust the `ConfigurableParam` in the `Batcher` class to refer to any class that derives from `Augmenter`:

```
import random
from scooch import Configurable
from scooch import Param
import numpy as np
from .augmenters import Augmenter

class Batcher(Configurable):
    """
    Constructs mini-batches for gradient descent.
    """

    _batch_size = Param(int, default=128, doc="The number of samples in each mini-batch")
    _audio_samples_per_smaple = Param(int, default=1024, doc="The number of audio samples to extract each feature from")
    _augmenter = ConfigurableParam(Augmenter, doc="An augmentation transformation to be applied to each sample")

...
```

The `config.yaml` file now specifies which type of `Augmenter` to use, and may configure the parameters of that class and any of it's `Configurable` base classes:

```
Batcher:
    batch_size: 8
    augmenter:
        NoiseAugmenter:
            augmentations_per_sample: 2
            min_noise: -5.0
            max_noise: 5.0
```

The `batch_it.py` script can be run again and will now produce two unique noise augmentations for each sample drawn from the data source.

6 - Abstraction and Polymorphism
---

Now that there is a class hierarchy set up for `Augmenter`s, we can add new types of augmenters as we please. Because the interface and common parameters are defined in the base `Augmenter` class, the `Batcher` class will know how to use them, without any changes to that code.

Let's create a `DCOffsetAugmenter` to provide training examples with a non-zero offset. Add the following class to `./batcher/augmenters.py`:

```
class DCOffsetAugmenter(Augmenter):
    """
    Adds random DC offsets to training samples.
    """

    _offset_variance = Param(float, default=1.0, doc="The variance of random offset values applied as data augmentations")

    def _get_augmentation(self, sample):
        return sample + np.random.normal(scale=np.sqrt(self._offset_variance), size=sample.shape)
```

Simply by defining this class we can "select" it in the `./config.yaml` file like so:

```
Batcher:
    batch_size: 8
    augmenter:
        DCOffsetAugmenter:
            augmentations_per_sample: 2
            offset_variance: 0.8
```

By running `batch_it.py` again, we will see that there is no longer additive noise in the batches, but constant offsets.

7 - Explore Scooch hierarchies with the CLI
---

As codebases and class hierarchies grow, the number of configuration options can become daunting. To help with onboarding to a codebase that uses scooch, you can view the options for a given Configurable base class as follows:

```
scooch options -m batcher -f Augmenter
```

This will print out the doc strings for all subclasses of `Augmenter` in the `batcher` module, including the Scooch parameter information.

Note that any module here will have to be installed or in your python path. If you receive a `ModuleNotFoundError`, you can add the batcher module to your python path like so:

```
export PYTHONPATH=$PYTHONPATH:`pwd`
```

Furthermore, the structure of configuration for a `Configurable` can become quite complex. To help new developers, it is recommender to include an example `config.yaml` file in your codebase. Alternatively, there is a wizard to produce `config.yaml` files for a given class, via the CLI.

```
scooch construct -c ./default_config.yaml -m batcher -f Batcher
```

This will prompt for the type of each `ConfigurableParam` and construct a configuration for the `Batcher` class in the `batcher` module and place it in the file `./default_config.yaml`.
