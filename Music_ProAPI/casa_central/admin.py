from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from .models import *

admin.site.register(Categoria, MPTTModelAdmin)
admin.site.register(Producto)
admin.site.register(Tienda)
admin.site.register(OrdenPedido)
