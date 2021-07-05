from django import template

register = template.Library()


@register.simple_tag
def multiplicar(precio, valor):
    return round(precio * valor)


register.filter("multiplicar", multiplicar)
