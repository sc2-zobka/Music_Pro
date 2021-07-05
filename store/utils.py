import json

from .models import *


def cookieCart(request):

    try:
        cart = json.loads(request.COOKIES["cart"])
    except:
        cart = {}
        print("CART:", cart)

    items = []
    orden = {"get_cart_total": 0, "get_cart_items": 0}
    cartItems = orden["get_cart_items"]

    # fetch products in cart Cookie and pass them to cartItems
    for i in cart:
        try:
            cartItems += cart[i]["quantity"]

            producto = Producto.objects.get(id=i)
            total = producto.precio * cart[i]["quantity"]

            orden["get_cart_total"] += total
            orden["get_cart_items"] += cart[i]["quantity"]

            #
            # TO-DO: pasar a item{} solamente los campos usados en la vista "checkout"
            #
            item = {
                "id": producto.id,
                "producto": {
                    "id": producto.id,
                    "nombre": producto.nombre,
                    "precio": producto.precio,
                    "imagen": producto.imagen,
                },
                "cantidad": cart[i]["quantity"],
                "get_total": total,
            }
            items.append(item)
        except:
            pass

    return {"cartItems": cartItems, "orden": orden, "items": items}


def cartData(request):

    if request.user.is_authenticated:
        cliente = request.user.cliente
        orden, created = Orden.objects.get_or_create(cliente=cliente, es_completa=False)
        items = orden.ordenitem_set.all()
        cartItems = orden.get_cart_items
    else:
        # Empty cart for non-logged users
        cookieData = cookieCart(request)
        cartItems = cookieData["cartItems"]
        orden = cookieData["orden"]
        items = cookieData["items"]

    return {"cartItems": cartItems, "orden": orden, "items": items}


def guestOrden(request, data):

    print("User is not logged in")

    nombre = data["form"]["nombre"]
    apellido = data["form"]["apellido"]
    email = data["form"]["email"]
    telefono = data["form"]["telefono"]
    tienda = data["form"]["tienda"]

    # fetch cookie cart
    cookieData = cookieCart(request)
    items = cookieData["items"]

    # Create Cliente
    cliente, created = Cliente.objects.get_or_create(email=email)
    cliente.nombre = nombre

    # TO-DO: add [apellido, email, telefono]
    # telefono can be fetch from User linked to Cliente
    cliente.save()

    # Create Orden
    orden, created = Orden.objects.get_or_create(cliente=cliente, es_completa=False)

    # Append all products to a OrdenItem Object
    for item in items:
        producto = Producto.objects.get(id=item["id"])
        ordenItem = OrdenItem.objects.create(
            producto=producto,
            orden=orden,
            cantidad=item["cantidad"],
        )

    return cliente, orden
