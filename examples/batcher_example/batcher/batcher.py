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

import random
import numpy as np
from scooch import Configurable
from scooch import ConfigurableParam
from scooch import Param
from .augmenters import Augmenter

class Batcher(Configurable):
    """
    Constructs mini-batches for gradient descent.
    """

    _batch_size = Param(int, default=128, doc="The number of samples in each mini-batch")
    _audio_samples_per_smaple = Param(int, default=1024, doc="The number of audio samples to extract each feature from")
    _augmenter = ConfigurableParam(Augmenter, doc="An augmentation transformation to be applied to each sample")

    def set_data(self, data):
        # Save a reference to a data array, to sample / batch from
        self._data = data

    def get_batch(self):
        feature_data = []
        while len(feature_data) < self._batch_size:
            start_idx = np.random.randint(0, self._data.shape[0]-self._audio_samples_per_smaple)
            audio_segment = self._data[start_idx:(start_idx+self._audio_samples_per_smaple)]
            feature_data += [self._augmenter.augment(audio_segment)]
        random.shuffle(feature_data)
        return np.vstack(feature_data[:self._batch_size])
        