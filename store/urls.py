from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import (
    aceptar_pedido,
    carro,
    checkout,
    consultar_producto,
    contacto,
    detalle_producto,
    modificar_cliente,
    ordenes_pedido,
    pedido_detalle,
    procesar_orden,
    realizar_pedido,
    registro,
    tienda,
    transferencia,
    update_item,
)

urlpatterns = [
    path("", tienda, name="tienda"),
    path("carro/", carro, name="carro"),
    path("transferencia/", transferencia, name="transferencia"),
    path("checkout/", checkout, name="checkout"),
    path("contacto/", contacto, name="contacto"),
    path("registro/", registro, name="registro"),
    path("procesar_orden/", procesar_orden, name="procesar_orden"),
    path("update_item/", update_item, name="update_item"),
    path("modificar_cliente/<id>", modificar_cliente, name="modificar_cliente"),
    path("consultar_producto/", consultar_producto, name="consultar_producto"),
    path("ordenes_pedido/", ordenes_pedido, name="ordenes_pedido"),
    path("realizar_pedido/", realizar_pedido, name="realizar_pedido"),
    path("pedido_detalle/<id>", pedido_detalle, name="pedido_detalle"),
    path("aceptar_pedido/<id>", aceptar_pedido, name="aceptar_pedido"),
    path("detalle_producto/<id>", detalle_producto, name="detalle_producto"),
]
