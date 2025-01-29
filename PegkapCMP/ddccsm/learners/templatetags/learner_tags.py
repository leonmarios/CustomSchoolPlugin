from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary using bracket notation"""
    if dictionary is None:
        return None
    return dictionary.get(key)

@register.filter
def call(obj, method_name):
    """Call a method on an object with the given argument"""
    method = getattr(obj, method_name)
    if callable(method):
        return method()
    return method

@register.filter
def getattribute(form, field_name):
    """Gets a form field by its name"""
    try:
        return form[field_name]  # This returns the BoundField
    except (KeyError, AttributeError):
        return None

@register.filter
def split(value, arg):
    """Split a string into a list on the given delimiter"""
    return value.split(arg) 