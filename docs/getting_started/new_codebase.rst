.. _new_codebase:

Getting Started with a New Codebase
```````````````````````````````````````

If you are starting a new project, scooch is an easy way to keep your code structured and configurable as you develop. This example provides a walkthrough in starting a new Scooch configurable codebase for creating mini-batches to be used in a gradient descent algorithm. It highlights many of the features and benefits of using Scooch.

A completed version of this example is available in the `examples <https://github.com/PandoraMedia/scooch/tree/main/examples/batcher_example>`_ provided on github.

In this example we'll need a few python packages in our environment:

.. code-block:: bash

    pip install scooch numpy scipy matplotlib

Let's also create a directory to work in:

.. code-block:: bash

    mkdir ./scooch_getting_started
    cd ./scooch_getting_started

1 - Parameterize a class
''''''''''''''''''''''''''

A core componet of this code will be a configurable :code:`Batcher` class. To make a new scooch configurable class, you can simply inherit from :code:`scooch.Configurable` and define some parameters on that class's definition. For the :code:`Batcher` class, we'll start simple by placing the following class in :code:`./batcher.py`:

.. code-block:: python

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

This class will extract random samples from the provided test data.

2 - Write a config
''''''''''''''''''''''''''

Now that there is a class to configure, you can write a yaml file that will set its parameters, e.g., for the :code:`Batcher` class above:

.. code-block:: yaml

    Batcher:
        batch_size: 8

Save this as :code:`./config.yaml` in the current working directory.

Note that we need not configure a parameter if we want to use its default value. In this case we'll use the default for :code:`audio_samples_per_sample`. All parameters without a default value defined, are required to be specified in the config file.

Note that the :code:`batch_size` parameter is private to the batcher class, but no leading underscores are used in the config file. With Scooch classes it is preferred to keep parameters private to each class, and expose them as :code:`@property`\ s where necessary. However this is not required. For example, the :code:`_batch_size` parameter could equivalently be named :code:`batch_size` if the developer prefers public parameters.

3 - Construct and use the class
'''''''''''''''''''''''''''''''''''''''

At this point, it is simple to instantiate the class with the specified configuration file and execute methods on it. For example, a script to pull mini-batches from the :code:`Batcher` class could be as simple as:

.. code-block:: python

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

For this example, we'll simply plot the data, though this could easily be extended to do something more useful like dump the data to :code:`.npy` files for training a model.

Save this script as :code:`batch_it.py`, it can then be executed as:

.. code-block:: bash

    python ./batch_it.py --config ./config.yaml --data ./data/test_data.wav

There we have it, a script that uses scooch to configure a class for producing mini-batches. This can be done simply with many different python config libraries. Next we'll look into some of the benefits of Scooch's object oriented approach in particular.

4 - Encapsulation
''''''''''''''''''''''''''

One of the primary benefits of scooch is that it constructs not only classes, but entire class hierarchies, with minimal code. Perhaps we want the :code:`Batcher` class above to produce augmentations of the data source it is reading from. 

To get started it might make sense to place our :code:`Batcher` class in a python package. We can do this by organizing our previous files like so in the following directories:

.. code-block:: none

    ./batch_it.py
    ./config.yaml
    ./batcher/__init__.py
    ./batcher/batcher.py

and place the following in the :code:`./batcher/__init__.py` file:

.. code-block:: python

    from .batcher import Batcher

For data augmentations we'll like want to parameterize that augmentation itself. Let's create an augmenter class that takes in some feature data and augments it. Put the following in the file :code:`./batcher/augmenters.py`

.. code-block:: python

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

We can now employ this new :code:`Configurable` inside the :code:`Batcher` class by adding a :code:`ConfigurableParam` in the class definition of :code:`Batcher`, e.g., 

.. code-block:: python

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

Upon instantiation, this class will be constructed and assigned to the :code:`_augmenter` attribute, so using it is simple. We can adjust the :code:`get_batch` method of :code:`Batcher` to do this:

.. code-block:: python

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

We can now adjust the :code:`./config.yaml` to configure the new :code:`Configurable` class parameter:

.. code-block:: yaml

    Batcher:
        batch_size: 8
        augmenter:
            NoiseAugmenter:
                min_noise: -5.0
                max_noise: 5.0

Without any changes to the :code:`./batch_it.py` script, scooch will construct the new class hierarchy based on the parameters and configuration, to produce noise augmented samples. Try running the following again:

.. code-block:: bash

    python ./batch_it.py --config ./config.yaml --data ./data/test_data.wav

Here we can see that Scooch has constructed the new class hierarchy based on the updated configuration and produced batches of what are now noisy samples.

5 - Inheritance
''''''''''''''''''''''''''

Scooch configures not only classes, but class hierarchies. As this codebase develops it is likely that there'll be several different types of :code:`Augmenter`\ s. To support this, let's construct an :code:`Augmenter` base class that :code:`NoiseAugmenter` will inherit from. In this class we might also want to include some functionality that is common to all augmenters, e.g., the number of augmentations performed per input sample. To do this, adjust :code:`./augmenters.py` like so:

.. code-block:: python

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

We now adjust the :code:`ConfigurableParam` in the :code:`Batcher` class to refer to any class that derives from :code:`Augmenter`:

.. code-block:: python

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

The :code:`config.yaml` file now specifies which type of :code:`Augmenter` to use, and may configure the parameters of that class and any of it's :code:`Configurable` base classes:

.. code-block:: yaml

    Batcher:
        batch_size: 8
        augmenter:
            NoiseAugmenter:
                augmentations_per_sample: 2
                min_noise: -5.0
                max_noise: 5.0

The :code:`batch_it.py` script can be run again and will now produce two unique noise augmentations for each sample drawn from the data source.

6 - Abstraction and Polymorphism
'''''''''''''''''''''''''''''''''''''''

Now that there is a class hierarchy set up for :code:`Augmenter`\ s, we can add new types of augmenters as we please. Because the interface and common parameters are defined in the base :code:`Augmenter` class, the :code:`Batcher` class will know how to use them, without any changes to that code.

Let's create a :code:`DCOffsetAugmenter` to provide training examples with a non-zero offset. Add the following class to :code:`./batcher/augmenters.py`:

.. code-block:: python

    class DCOffsetAugmenter(Augmenter):
        """
        Adds random DC offsets to training samples.
        """

        _offset_variance = Param(float, default=1.0, doc="The variance of random offset values applied as data augmentations")

        def _get_augmentation(self, sample):
            return sample + np.random.normal(scale=np.sqrt(self._offset_variance), size=sample.shape)

Simply by defining this class we can "select" it in the :code:`./config.yaml` file like so:

.. code-block:: yaml

    Batcher:
        batch_size: 8
        augmenter:
            DCOffsetAugmenter:
                augmentations_per_sample: 2
                offset_variance: 0.8

By running :code:`batch_it.py` again, we will see that there is no longer additive noise in the batches, but constant offsets.

7 - Explore Scooch hierarchies with the CLI
''''''''''''''''''''''''''''''''''''''''''''''''''''

As codebases and class hierarchies grow, the number of configuration options can become daunting. To help with onboarding to a codebase that uses scooch, you can view the options for a given Configurable base class as follows:

.. code-block:: bash

    scooch options -m batcher -f Augmenter

This will print out the doc strings for all subclasses of :code:`Augmenter` in the :code:`batcher` module, including the Scooch parameter information.

Note that any module here will have to be installed or in your python path. If you receive a :code:`ModuleNotFoundError`, you can add the batcher module to your python path like so:

.. code-block:: bash

    export PYTHONPATH=$PYTHONPATH:`pwd`

Furthermore, the structure of configuration for a :code:`Configurable` can become quite complex. To help new developers, it is recommender to include an example :code:`config.yaml` file in your codebase. Alternatively, there is a wizard to produce :code:`config.yaml` files for a given class, via the CLI.

.. code-block:: bash

    scooch construct -c ./default_config.yaml -m batcher -f Batcher

This will prompt for the type of each :code:`ConfigurableParam` and construct a configuration for the :code:`Batcher` class in the :code:`batcher` module and place it in the file :code:`./default_config.yaml`.
