from django import template

register = template.Library()

@register.filter
def add_class(field, css_class):
    """Adds a CSS class to a form field widget."""
    return field.as_widget(attrs={"class": css_class})
