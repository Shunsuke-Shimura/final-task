from django import template

register = template.Library()

@register.filter
def retm33t_state(tm33t, user):
    """Returns tm33t's retm33t state as string (retm33ted or unretm33ted)"""
    if tm33t.has_been_retm33ted(user):
        return 'retm33ted'
    return 'unretm33ted'
