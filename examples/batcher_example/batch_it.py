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
