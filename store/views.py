import datetime
import json

import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group, User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt

from .forms import (
    ContactoForms,
    CustomUserCreationForm,
    ModificarClienteForms,
    PedidoCasaCentralForms,
)
from .models import *
from .utils import cartData, cookieCart, guestOrden


def update_item(request):
    data = json.loads(request.body)
    productId = data["productId"]
    action = data["action"]

    cliente = request.user.cliente
    producto = Producto.objects.get(id=productId)
    orden, created = Orden.objects.get_or_create(cliente=cliente, es_completa=False)

    ordenItem, created = OrdenItem.objects.get_or_create(orden=orden, producto=producto)

    if action == "add":
        ordenItem.cantidad = ordenItem.cantidad + 1
    elif action == "remove":
        ordenItem.cantidad = ordenItem.cantidad - 1

    ordenItem.save()

    if ordenItem.cantidad <= 0:
        ordenItem.delete()

    return JsonResponse("Item was added", safe=False)


def tienda(request):

    cart_data = cartData(request)

    cartItems = cart_data["cartItems"]
    orden = cart_data["orden"]
    items = cart_data["items"]

    productos = Producto.objects.all()
    data = {
        "productos": productos,
        "cartItems": cartItems,
    }
    return render(request, "store/tienda.html", data)


def carro(request):

    cart_data = cartData(request)

    cartItems = cart_data["cartItems"]
    orden = cart_data["orden"]
    items = cart_data["items"]

    data = {
        "items": items,
        "orden": orden,
        "cartItems": cartItems,
    }

    return render(request, "store/carro.html", data)


def checkout(request):

    cart_data = cartData(request)

    cartItems = cart_data["cartItems"]
    orden = cart_data["orden"]
    items = cart_data["items"]

    tiendas = Tienda.objects.all()

    data = {
        "items": items,
        "orden": orden,
        "cartItems": cartItems,
        "tiendas": tiendas,
    }

    return render(request, "store/checkout.html", data)


def contacto(request):
    data = {"form": ContactoForms()}

    if request.method == "POST":
        formulario = ContactoForms(data=request.POST)

        if formulario.is_valid():
            formulario.save()

            messages.success(request, "Contacto enviado!")

            return render(request, "store/contacto.html", data)
        data["form"] = formulario

    return render(request, "store/contacto.html", data)


def transferencia(request):

    if request.user.is_authenticated:
        cliente = request.user.cliente
        orden, created = Orden.objects.get_or_create(cliente=cliente, es_aceptada=False)

    else:
        # Empty cart for non-logged users
        items = []
        orden = {"get_cart_total": 0, "get_cart_items": 0}
        cartItems = orden["get_cart_items"]

    data = {
        "orden": orden,
    }

    return render(request, "store/transferencia.html", data)


def realizar_pedido(request):
    data = {"form": PedidoCasaCentralForms()}

    if request.method == "POST":
        formulario = PedidoCasaCentralForms(data=request.POST)

        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Pedido a Casa Central enviado!")

            url = "http://localhost:8010/api/v1/ordenes-de-pedido/"
            payload = request.POST

            try:
                requests.post(url, json=payload)
            except Exception:
                # add validation error in case of a denied request (AKA: 4## or 5##)
                pass

            return render(request, "store/realizar_pedido.html", data)

    return render(request, "store/realizar_pedido.html", data)


def registro(request):
    data = {"form": CustomUserCreationForm()}

    if request.method == "POST":
        formulario = CustomUserCreationForm(data=request.POST)

        if formulario.is_valid():
            formulario.save()

            #
            # Asociar con un registro de cliente
            #
            cliente = Cliente()
            cliente.cliente = User.objects.get(email=formulario.cleaned_data["email"])
            cliente.nombre = username = formulario.cleaned_data["nombre"]
            cliente.email = formulario.cleaned_data["email"]

            grupo = Group.objects.get(name="Cliente")
            cliente.cliente.groups.add(grupo)

            #
            # Guardar Cliente
            #
            cliente.save()

            login(request, cliente.cliente)
            return redirect(to="tienda")

        data["form"] = formulario

    return render(request, "registration/registro.html", data)


@login_required
@permission_required({"store.change_cliente", "store.view_cliente"})
def modificar_cliente(request, id):
    if not request.user.is_staff:
        cliente = get_object_or_404(Cliente, cliente_id=id)
        usuario = get_object_or_404(User, id=id)

        context = {
            "nombre": cliente.nombre,
            "email": cliente.email,
            "nombre_usuario": usuario.username,
        }

        data = {"form": ModificarClienteForms(data=context)}

        if request.method == "POST":
            formulario = ModificarClienteForms(data=request.POST, instance=cliente)

            if formulario.is_valid():
                formulario.save()
                return redirect(to="tienda")

            data["form"] = formulario

        return render(request, "registration/modificar_cliente.html", data)
    else:
        return redirect("/")


@login_required
@permission_required("store.view_producto")
def consultar_producto(request):
    data = {"productos": Producto.objects.all()}

    if request.method == "POST":
        codigo_producto = request.POST["cod-prod"]
        url = str()

        if codigo_producto:
            url = "http://localhost:8010/api/productos/?codigo_producto=" + str(codigo_producto)
        else:
            url = "http://localhost:8010/api/productos/"
        try:
            response = requests.get(url)

            b = json.loads(response.text)
            data["productos_response"] = b
        except Exception:
            pass

    return render(request, "store/consultar_producto.html", data)


@login_required
@permission_required({"store.view_orden", "store.change_orden"})
def ordenes_pedido(request):
    grupo = request.user.groups.get(user=request.user.id)

    data = {
        "ordenes": Orden.objects.filter(es_aceptada=False),
        "tipo_usuario": str(grupo),
    }

    if str(grupo) == "Vendedor":

        pass
        # data["form"] = OrdenPedidoForms
        # data["form_cliente"] = ClientePedidoForms
    elif str(grupo) == "Bodeguero":

        if request.method == "POST":

            try:
                orden = Orden.objects.get(pk=request.POST["orden-id"])
                orden.es_aceptada = True
                orden.save()

                if orden.retiro_en_tienda:
                    pass
                else:
                    pass
            except Exception:
                pass

    return render(request, "store/ordenes_pedido.html", data)


@login_required
@permission_required("store.view_orden")
def pedido_detalle(request, id):
    data = {"items": OrdenItem.objects.filter(orden=id)}

    return render(request, "store/orden_pedido.html", data)


@login_required
@permission_required({"store.view_orden", "store.change_orden"})
def aceptar_pedido(request, id):
    orden = get_object_or_404(Orden, id=id)
    data = {}

    if request.method == "POST":
        if orden is not None:
            orden.es_aceptada = True
            orden.save()
            data["mensaje"] = "Orden de pedido aceptada"

    return render(request, "store/ordenes_pedido.html", data)


def detalle_producto(request, id):
    producto = Producto.objects.filter(id=id).first()
    # data = {
    #     "producto": Producto.objects.filter(id=id)
    # }
    data = {}
    data["producto"] = producto

    return render(request, "store/detalle_producto.html", data)


@csrf_exempt
def procesar_orden(request):

    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    print(data["form"])

    if request.user.is_authenticated:

        cliente = request.user.cliente
        orden, created = Orden.objects.get_or_create(cliente=cliente, es_completa=False)

    else:

        cliente, orden = guestOrden(request, data)

        # print("User is not logged in")

        # # Not Shipping
        # nombre = data["form"]["nombre"]
        # apellido = data["form"]["apellido"]
        # email = data["form"]["email"]
        # telefono = data["form"]["telefono"]
        # tienda = data["form"]["tienda"]

        # # fetch cookie cart
        # cookieData = cookieCart(request)
        # items = cookieData["items"]

        # # Create Cliente
        # cliente, created = Cliente.objects.get_or_create(email=email)
        # cliente.nombre = nombre
        # # TO-DO: add [apellido, email, telefono]
        # # telefono can be fetch from User linked to Cliente
        # cliente.save()

        # # Create Orden
        # orden, created = Orden.objects.get_or_create(cliente=cliente, es_completa=False)

        # # Append all products to a OrdenItem Object
        # for item in items:
        #     producto = Producto.objects.get(id=item["id"])
        #     ordenItem = OrdenItem.objects.create(
        #         producto=producto,
        #         orden=orden,
        #         cantidad=item["cantidad"],
        #     )

    # fetch cart total from the FrontEnd
    total = int(data["form"]["total"])

    # Set transaction_id in Orden
    orden.transaction_id = transaction_id

    # check if total sent by frontend is equal to total in backend
    if total == int(orden.get_cart_total):
        # Orden turns completed
        orden.es_completa = True

    # check if takeaway is needed
    despacho = data["shipping"]["despacho"]
    if despacho is None:
        orden.retiro_en_tienda = True

    orden.save()

    # check Orden paid and Takeaway needed
    if orden.es_completa == True and orden.retiro_en_tienda == False:

        OrdenDeDespacho.objects.create(
            cliente=cliente,
            orden=orden,
            direccion=data["shipping"]["direccion"],
            ciudad=data["shipping"]["ciudad"],
            comuna=data["shipping"]["comuna"],
            region=data["shipping"]["region"],
            zipcode=data["shipping"]["zipcode"],
        )

    # TO-DO:
    # if orden.es_completa == True and orden.retiro_en_tienda == True:
    #
    # Sent email informing store location (Vitacura, Maipu or Providencia)
    # where Cliente needs to get his products

    # TO-DO: sent email confirmation to Cliente

    return JsonResponse("Pago realizado..", safe=False)
