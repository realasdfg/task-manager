from django import template

register = template.Library()


@register.filter
def priority_badge(priority):
    return {
        "urgent": "bg-danger",
        "high": "bg-warning text-dark",
        "medium": "bg-tertiary",
        "low": "bg-success",
    }.get(priority, "bg-tertiary")
