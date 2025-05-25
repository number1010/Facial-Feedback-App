from django import template
from decimal import Decimal

register = template.Library()

@register.filter(name='currency_vnd')
def currency_vnd(value):
    if not value:
        return "0 VND"
    try:
        value = Decimal(value)
        formatted = "{:,.0f}".format(value)
        # Replace comma with dot for thousand separators
        formatted = formatted.replace(',', '.')
        return f"{formatted} VND"
    except (ValueError, TypeError):
        return "0 VND"