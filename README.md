Configipy
===
A small library to assist with creating classes that are configurable via yaml files.

Sometimes it's just easier to read a yaml file for an experiment configuration than searchig through code.

The idea is to have a light wrapper around loading yaml files into dictionaries, and an interface for classes whose attributes are set by these yaml dictionaries.

This provides a couple of advantages over direct python object configuration with something like `ruamel.yaml`:
 - It allows you to dump no only classes but hierarchies of classes to file
 - It is designed to provide an easy way to define classes by manually writing yaml files rather than saving and alter loading yaml files
 - It allows you to simply specify the parameters that are important to save to yaml, preventing saving of large data structures such as matrices
 - It allows default parameters - important for backwards compatibility when adding new configuration parameters to a pre-existing configurable class

For example a configuration object is created via:

```
from config import Config

cfg = Config('filename.yaml')
```

where "filename.yaml" exists at the end of the filename of the desired yaml file.

Configurable objects are a subclass of the Configurable class. For example a class with a `class_configuration.yaml` yaml file:

```
# This yaml file is for a class with a batch size parameter

ConfigurableSubclass:
    _batch_size: 128
```

Could be configured like so:

```
from config import Configurable
from config import Config

class ConfigurableSubclass(Configurable):

	def PrintBatchSize(self):
		print(str(self._batch_size))

cfg = Config('class_configuration.yaml')

example = ConfigurableSubclass(cfg['experiment_config'])
example.PrintBatchSize()
```

This should output `128`.
