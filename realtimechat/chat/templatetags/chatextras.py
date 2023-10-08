from django import template
register = template.Library()


@register.filter(name = 'initials')
def initials(value):
    initials = ''
    splitted_name = value.split(' ')
    if len(splitted_name) > 1:
        first_name = splitted_name[0]
        last_name = splitted_name[-1]
        initials = first_name[0].upper() + last_name[0].upper()
    else:
        initials += splitted_name[0][0]

    return initials