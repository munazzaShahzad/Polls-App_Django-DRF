from django import template

register = template.Library()


@register.inclusion_tag('polls/display_polls.html')
def show_polls(polls):
    return {'polls': polls}
