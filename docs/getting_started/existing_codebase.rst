.. _existing_codebase:

Getting Started with an Existing Codebase
````````````````````````````````````````````````````

Depending on your requirements, there are a few ways to make your existing code Scooch configurable. In most cases the :code:`scooch.configurize` will be a key piece of functionality.

Configurizing Classes that You Own
''''''''''''''''''''''''''''''''''

If you already have class definitions in your code that you want to make configurable, you can use the :code:`configurize` decorator:

.. code-block:: python

    from scooch import configurize

    @configurize
    class PreexistingClass(object):

        def __init__(self, arg1, arg2=5)
            ...

Scooch will create a derived class that has :code:`arg1` and :code:`arg2` as configurable parameters, with a default value of :code:`5` for :code:`arg2`. The derived class will take a Scooch :code:`Config` dictionary in the constructor argument, like any other Scooch :code:`Configurable`.

Note that Scooch will prefix :code:`Scooch` to the class name to differentiate it from the non-configurable version of the class. For example, in your Scooch :code:`config.yaml` file, the type of the configurized class above will be :code:`ScoochPreexistingClass`

You can also add a class to an existing Scooch :code:`Configurable` hierarchy, by specifying a :code:`base_class` that is also a :code:`Configurable`.

.. code-block:: python

    @configurize(base_class=ScoochConfigurableBaseClass)
    class PreexistingClass(object):

        def __init__(self, arg1, arg2=5)

Configurizing Third-Party Classes
'''''''''''''''''''''''''''''''''

If the class you want to configure with Scooch belongs to a code base you are not a contributor for, you will have no access to modify the class definition. One way to make a third party class Scooch configurable is to use :code:`scooch.configurize`.

For example, if you are developing an ML training pipeline, you may want to use the classes in :code:`tensorflow.keras.losses`, and parameterize them in your Scooch config file. Making a single third party class configurable is as easy as:

.. code-block:: python

    from scooch import configurize
    import tensorflow as tf

    configurable_class = configurize(tf.keras.losses.BinaryCrossEntropy)

We can now write a :code:`./config.yaml` for this new class:

.. code-block:: yaml

    ScoochBinaryCrossEntropy:
        from_logits: True
        label_smoothing: 0.5

The new configurable loss may be instantiated and used like any other keras loss function.

.. code-block:: python

    ...

    from scooch import Config

    loss_func = configurable_class(Config('./config.yaml'))

    ...

This will create a single configurable class that is currently isolated to it's own inheritance hierarchy. Perhaps you want to create a range of :code:`Loss` functions, some custom and some derived from a third party, that will be selectable in your :code:`config.yaml` like any other Scooch type. Scooch can do this through multiple inheritence, by adding a user defined Scooch base class to each :code:`congigurize`\ d third party class:


For example, to add all keras loss functions to our Scooch hierarchy we could do the following:

.. code-block:: python

    from scooch import Configurable
    from scooch import configurize
    import sys
    import inspect

    class Loss(Configurable):
        """
        Base class for all Scooch Configurable loss functions.
        """

        pass

    clsmembers = inspect.getmembers(sys.modules[tf.keras.losses.__name__], inspect.isclass)
    configurable_tf_losses = [configurize(mem[0], Loss) for mem in clsmembers if mem[0] != 'Loss']

With the above code, classes can now be defined with a :code:`Param` of type :code:`Loss`, which will now be able to use all keras loss functions in your :code:`config.yaml` file:

.. code-block:: python

    ...

    from scooch import Param

    class Experiment(Configurable):

        Param(Loss, doc="A Loss function to train a model with.")
        ...

Configurizing Code that is not Object Oriented
''''''''''''''''''''''''''''''''''''''''''''''

We are currently working on extending Scooch to configure functional code.

If you're convinced by the arguments in :ref:`benefits` section, you may want to start trying to structure your code using object oriented programming.

An easy start to transforming your code into an object oriented structure, can be to first place it in a :code:`run()` method of a Scooch :code:`Configurable`. For example,

.. code-block:: python

    from scooch import Configurable
    from scooch import Config

    class Experiment(Configurable):
        """
        The class that encapsulates my ML task.
        """

        def run():
            # Your code here.

    experiment = Experiment(Config('./config.yaml'))
    experiment.run()

From here, you might want to start breaking out configurable parameters as :code:`scooch.Param`\ s, separate functionality into separate methods, and create classes used within the :code:`Experiment` class to modularize some of its processes. 

If Scooch looks like something you want to use, but it does not meet your needs, you can file a `feature request <https://github.com/PandoraMedia/scooch/issues>`_.
