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


@register.simple_tag
def query_transform(request, **kwargs):
    updated = request.GET.copy()
    for key, value in kwargs.items():
        if value is not None:
            updated[key] = value
        else:
            updated.pop(key, 0)
    return updated.urlencode()


@register.simple_tag
def page_query(request, page_param, page_number):
    updated = request.GET.copy()
    updated[page_param] = page_number
    return updated.urlencode()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
