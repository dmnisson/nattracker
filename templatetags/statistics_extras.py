from django import template

register = template.Library();

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def field_type(field):
    return field.field.widget.__class__.__name__;

@register.filter
def field_css_class(field):
    if (field_type(field) == "Select" or field_type(field) == "SelectMultiple"):
        return "custom-select";
    elif (field_type(field) == "CheckboxInput"):
        return "form-check-input"
    else:
        return "form-control";