from django import template
register = template.Library()

@register.filter
def inrange(value):
    return range(value)
