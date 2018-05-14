from urllib.parse import urlencode

from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    """Template helper that uses to avoid params duplication"""
    query = context['request'].GET.dict()
    query.update(kwargs)
    return urlencode(query)


@register.simple_tag(takes_context=True)
def to_array(context, **kwargs):
    """Template helper that conver query dict to array"""
    queryarray = context['request'].GET.dict().items()
    return queryarray


@register.filter(name='zip')
def zip_lists(a, b):
    return zip(a, b)
