"""
Created 11-13-20 by Matt C. McCallum
"""


# Local imports
# None.

# Third party imports
# None.

# Python standard library imports
import textwrap


class ConfigMeta(type):
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
        # Get all base classes that are also ConfigMeta types
        meta_bases = [base for base in bases if type(base) is ConfigMeta]

        # Collect all params from base classes
        params = {k:v for base in meta_bases for k, v in base.__PARAMS__.items()}
        if '__PARAMS__' in attrs.keys():
            params = {**params, **attrs['__PARAMS__']}
        attrs['__PARAMS__'] = params

        # Collect all defaults from base classes
        default_params = {k:v for base in meta_bases for k, v in base.__PARAM_DEFAULTS__.items()}
        if '__PARAM_DEFAULTS__' in attrs.keys():
            default_params = {**default_params, **attrs['__PARAM_DEFAULTS__']}
        attrs['__PARAM_DEFAULTS__'] = default_params

        # Update the docs
        if len(list(attrs['__PARAMS__'].keys())):
            attrs['__doc__'] += textwrap.indent(textwrap.dedent("""

            **Configipy Parameters**:
            """), '    ')

        for param, doc in attrs['__PARAMS__'].items():
            if param in list(attrs['__PARAM_DEFAULTS__'].keys()):
                param_value = attrs['__PARAM_DEFAULTS__'][param]
                if '\n' in str(param_value) or len(str(param_value)) > 40:
                    param_value = f" (Default is of type {type(param_value)})"
                else:
                    default_info = f" (Default: {attrs['__PARAM_DEFAULTS__'][param]})"
            else:
                default_info = ""
            doc_addition = textwrap.indent(textwrap.dedent(f"""
            **{param}**{default_info}:
                {textwrap.fill(doc, 400)}
            """), '    ')
            attrs['__doc__'] += doc_addition

        return super(ConfigMeta, cls).__new__(cls, name, bases, attrs)
