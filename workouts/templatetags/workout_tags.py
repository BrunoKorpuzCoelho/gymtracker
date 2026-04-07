from django import template
import json

register = template.Library()


@register.filter(name='json_script_raw')
def json_script_raw(value):
    """Safely output a Python dict/list as JSON string."""
    if isinstance(value, str):
        return value
    return json.dumps(value)
