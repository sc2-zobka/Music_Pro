from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from .models import *

admin.site.register(Categoria, MPTTModelAdmin)
admin.site.register(Cliente)
admin.site.register(Producto)
admin.site.register(Orden)
admin.site.register(OrdenDeDespacho)
admin.site.register(Tienda)
admin.site.register(OrdenItem)
admin.site.register(Contacto)
admin.site.register(PedidoCasaCentral)
