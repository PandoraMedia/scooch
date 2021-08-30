"""
Created 11-13-20 by Matt C. McCallum
"""


# Python standard library imports
import textwrap
import inspect

# Third party imports
# None.

# Local imports
# None.


class ConfigurableMeta(type):
    """
    Metaclass for configipy configurables. Enables programmatic modification
    to the classes for things like programmatic class documentation.
    """

    def __new__(cls, name, bases, attrs):
        """
        Preconstructor.

        Currently does two things:
            - Collects all parameters and parameter defaults through the Configurable inheretence hierarchy
            - Updates the class doc string with information on its configipy parameters
        """
        # Get all base classes that are also ConfigurableMeta types
        meta_bases = [base for base in bases if type(base) is ConfigurableMeta]

        # Collect all params from base classes
        cls._collect_param_from_bases(meta_bases, attrs, '__PARAMS__')
        cls._collect_param_from_bases(meta_bases, attrs, '__PARAM_DEFAULTS__')
        cls._collect_param_from_bases(meta_bases, attrs, '__CONFIGURABLES__')

        # Update the docs
        if len(list(attrs['__PARAMS__'].keys())):
            attrs['__doc__'] += textwrap.indent(textwrap.dedent("""

            **Configipy Parameters**:
            """), '    ')

        if '__PARAM_DOCS__' not in attrs:
            attrs['__PARAM_DOCS__'] = ''
        for param, doc in attrs['__PARAMS__'].items():
            if param in list(attrs['__CONFIGURABLES__'].keys()):
                param_cls = attrs['__CONFIGURABLES__'][param]
                if inspect.isclass(param_cls):
                    default_info = f" (Configurable: {attrs['__CONFIGURABLES__'][param].__name__})"
                else:
                    # TODO [matt.c.mccallum 03.31.21]: Handle the case of ConfigList and ConfigCollection below...
                    default_info = ""
            elif param in list(attrs['__PARAM_DEFAULTS__'].keys()):
                param_value = attrs['__PARAM_DEFAULTS__'][param]
                if '\n' in str(param_value) or len(str(param_value)) > 40:
                    param_value = f" (Default is of type {type(param_value)})"
                else:
                    default_info = f" (Default: {attrs['__PARAM_DEFAULTS__'][param]})"
            else:
                default_info = ""
            attrs['__PARAM_DOCS__'] += textwrap.indent(textwrap.dedent(f"""
                                                **{param}**{default_info}:
                                                    {textwrap.fill(doc, 400)}
                                                """), '    ')
        attrs['__doc__'] += attrs['__PARAM_DOCS__']

        return super(ConfigurableMeta, cls).__new__(cls, name, bases, attrs)

    @staticmethod
    def _collect_param_from_bases(meta_bases, attrs, param_name):
        """
        Collects a parameter from the attributes of all the provided base classes.

        Args:
            meta_bases: list(Configurable) - A list of base classes from which to collect the parameters.
            This is to be provided in order of inheritance.

            attrs: dict - A dictionary of all attributes for this class that inherits the provided bases.

            param_name: str - The name of the parameter to collect across all provided base classes.
        """
        # Reverse list here to respect the python method resolution order (MRO) in any comprehension statements.
        meta_bases = meta_bases[::-1]
        # Collect the params.
        params = {k:v for base in meta_bases for k, v in base.__dict__[param_name].items()}
        if param_name in attrs.keys():
            params = {**params, **attrs[param_name]}
        attrs[param_name] = params
