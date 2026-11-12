from django import template

register = template.Library()


@register.filter
def clp(valor):
    """12345 -> $12.345"""
    try:
        return "$" + f"{int(valor):,}".replace(",", ".")
    except (TypeError, ValueError):
        return "$0"
