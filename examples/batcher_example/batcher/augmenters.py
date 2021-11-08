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

class DCOffsetAugmenter(Augmenter):
    """
    Adds random DC offsets to training samples.
    """

    _offset_variance = Param(float, default=1.0, doc="The variance of random offset values applied as data augmentations")

    def _get_augmentation(self, sample):
        return sample + np.random.normal(scale=np.sqrt(self._offset_variance))

class NoiseAugmenter(Augmenter):
    """
    Takes in audio samples and augments them by adding noise, distributed uniformly on
    a logarithmic scale between the minimum and maximum provided noise values.
    """

    _noise_min = Param(float, default=-10.0, doc="Minimum RMS power of noise to be added to an audio sample (in dB)")
    _noise_max = Param(int, default=10.0, doc="Maximum RMS power of noise to be added to an audio sample (in dB)")

    def _get_augmentation(self, sample):
        # Produce a random dB value for the noise
        power_db = np.random.rand()*(self._noise_max - self._noise_min) + self._noise_min
        # Convert to linear
        power_linear = 10.0**(power_db/10.0)
        # Synthesize and add the noise to the signal
        noise_data = np.random.normal(scale=power_linear, size=sample.shape)
        return sample + noise_data
