from django.urls import path

from .views import (
    aceptar_pedido,
    cambiar_contrasena,
    carro,
    checkout,
    consultar_producto,
    contacto,
    detalle_producto,
    loguear,
    modificar_cliente,
    ordenes_pedido,
    pedido_detalle,
    realizar_pedido,
    registro,
    seleccionar_moneda,
    tienda,
    update_item,
)

urlpatterns = [
    path("", tienda, name="tienda"),
    path("carro/", carro, name="carro"),
    path("checkout/", checkout, name="checkout"),
    path("contacto/", contacto, name="contacto"),
    path("registro/", registro, name="registro"),
    path("update_item/", update_item, name="update_item"),
    path("modificar_cliente/<id>", modificar_cliente, name="modificar_cliente"),
    path("consultar_producto/", consultar_producto, name="consultar_producto"),
    path("ordenes_pedido/", ordenes_pedido, name="ordenes_pedido"),
    path("realizar_pedido/", realizar_pedido, name="realizar_pedido"),
    path("pedido_detalle/<id>", pedido_detalle, name="pedido_detalle"),
    path("aceptar_pedido/<id>", aceptar_pedido, name="aceptar_pedido"),
    path("detalle_producto/<id>", detalle_producto, name="detalle_producto"),
    path("accounts/login/", loguear, name="login"),
    path("accounts/change_password/", cambiar_contrasena, name="change_password"),
    path("seleccionar_moneda/<str:codigo>/", seleccionar_moneda, name="seleccionar_moneda"),
]
