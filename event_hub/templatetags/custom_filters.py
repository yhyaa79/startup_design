# event_hub/templatetags/custom_filters.py

from django import template

register = template.Library()

@register.filter
def is_list(value):
    """بررسی اینکه آیا مقدار یک لیست است"""
    return isinstance(value, list)
