import json

import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import Group, User
from django.core import serializers
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

# PRUEBA
from transbank.webpay.webpay_plus import transaction

from .forms import (
    ContactoForms,
    CustomCambioContrasenaForm,
    CustomUserCreationForm,
    ModificarClienteForms,
    PedidoCasaCentralForms,
)
from .models import *


def update_item(request):
    data = json.loads(request.body)
    productId = data["productId"]
    action = data["action"]
    # # # # # # # # # # # # # # # # # # #
    print("Action", action)
    print("Product", productId)
    # # # # # # # # # # # # # # # # # # #

    cliente = request.user.cliente
    producto = Producto.objects.get(id=productId)
    orden, created = Orden.objects.get_or_create(cliente=cliente, es_completa=False)
    ordenItem, created = OrdenItem.objects.get_or_create(orden=orden, producto=producto)

    if action == "add":
        ordenItem.cantidad += 1
    elif action == "remove":
        ordenItem.cantidad -= 1

    ordenItem.save()

    if ordenItem.cantidad <= 0:
        ordenItem.delete()

    return JsonResponse("Item was added", safe=False)


def seleccionar_moneda(request, codigo):
    request.session["CURRENCY_CODE"] = codigo
    print(request.session["CURRENCY_CODE"])

    # del request.session["AMT_CONVERSION"]

    if not "AMT_CONVERSION" in request.session:
        respuesta = requests.get(
            "https://api.exchangeratesapi.io/v1/latest?access_key=6c8a76e635e052fad1fd4be70b390b0b&base=CLP"
        )
        datos = respuesta.json()
        valores_cambios = datos["rates"]

        request.session["AMT_CONVERSION"] = valores_cambios

        denominaciones = {}

        for moneda in request.session["CURRENCY_CODES"]:
            for valor_cambio in request.session["AMT_CONVERSION"]:
                if moneda["fields"]["codigo_moneda"] == valor_cambio:
                    denominaciones[valor_cambio] = float(
                        request.session["AMT_CONVERSION"][moneda["fields"]["codigo_moneda"]]
                    )
                    break

        request.session["AMT_CONVERSION"] = denominaciones

    print(request.session["AMT_CONVERSION"])

    return redirect("tienda")


def tienda(request):
    cartItems = 0
    valor_cambio = 1

    if not "CURRENCY_CODE" in request.session:
        request.session["CURRENCY_CODE"] = "CLP"

    print(request.session["CURRENCY_CODE"])

    if request.user.is_authenticated:
        try:
            if not request.user.is_staff:
                cliente = request.user.cliente
                # params of get_or_create() must be fields of the Orden model
                orden, created = Orden.objects.get_or_create(cliente=cliente, es_aceptada=False)
                items = orden.ordenitem_set.all()
                cartItems = orden.get_cart_items
        except Exception as e:
            print(e)
    else:
        # Empty cart for non-logged users
        items = []
        orden = {"get_cart_total": 0, "get_cart_items": 0}
        cartItems = orden["get_cart_items"]

    productos = Producto.objects.all()
    monedas = None

    if not "CURRENCY_CODES" in request.session:
        monedas = Moneda.objects.all()

        tmp_json = serializers.serialize("json", monedas)

        request.session["CURRENCY_CODES"] = json.loads(tmp_json)
        print(request.session["CURRENCY_CODES"])

    if "AMT_CONVERSION" in request.session:
        valor_cambio = float(request.session["AMT_CONVERSION"][request.session["CURRENCY_CODE"]])

    data = {
        "productos": productos,
        "cartItems": cartItems,
        "monedas": monedas,
        "valor_cambio": valor_cambio,
    }

    return render(request, "store/tienda.html", data)


def carro(request):
    # cart for logged in users
    if request.user.is_authenticated:
        cliente = request.user.cliente
        # params of get_or_create() must be fields of the Orden model
        orden, created = Orden.objects.get_or_create(cliente=cliente, es_aceptada=False)
        items = orden.ordenitem_set.all()
        cartItems = orden.get_cart_items
    else:
        # cart for non-logged users
        items = []
        orden = {"get_cart_total": 0, "get_cart_items": 0}
        cartItems = orden["get_cart_items"]

    data = {
        "items": items,
        "orden": orden,
        "cartItems": cartItems,
    }

    return render(request, "store/carro.html", data)


def checkout(request):
    if request.user.is_authenticated:
        cliente = request.user.cliente
        # params of get_or_create() must be fields of the Orden model
        orden, created = Orden.objects.get_or_create(cliente=cliente, es_aceptada=False)
        items = orden.ordenitem_set.all()
        cartItems = orden.get_cart_items
    else:
        # Empty cart for non-logged users
        items = []
        orden = {"get_cart_total": 0, "get_cart_items": 0}
        cartItems = orden["get_cart_items"]

    data = {
        "items": items,
        "orden": orden,
        "cartItems": cartItems,
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


def loguear(request):
    data = {"form": AuthenticationForm()}

    if request.method == "POST":
        # here you get the post request username and password
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")

        # authentication of the user, to check if it's active or None
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                if not user.is_staff:
                    # this is where the user login actually happens, before this the user
                    # is not logged in.
                    login(request, user)

                    return redirect("tienda")
                else:
                    if user.last_login is None:
                        login(request, user)
                        messages.warning(request, "Como primer inicio se debe cambiar la contraseña")
                        return redirect("change_password")
                    else:
                        login(request, user)
                        return redirect("tienda")
            else:
                messages.error(request, "Usuario no disponible")
                return redirect("login")
        else:
            messages.error(request, "Usuario no disponible")
            return redirect("login")

    return render(request, "registration/login.html", data)


@login_required
def cambiar_contrasena(request):
    data = {"form": CustomCambioContrasenaForm(request.user)}

    if request.method == "POST":
        form = CustomCambioContrasenaForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, "Tu contraseña ha sido cambiada correctamente!")
            return redirect("change_password")
        else:
            messages.error(request, "La contraseña no se ha modificado.")
            return redirect("change_password")

    return render(request, "registration/cambiar_contrasena.html", data)


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
    if not request.user.is_staff and request.user.groups.filter(name="Cliente").exists():
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
        return redirect("/admin")


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


def webpay(request):
    monto = 2000
    orden_compra = 123456789
    sesion_id = "sessionId"

    url_regreso = "http://localhost:8000"
    url_final = "http://localhost:8000"

    response = transaction.Transaction.create(orden_compra, sesion_id, monto, url_regreso)

    token_ws = response.token
    token_accion = response.url

    data = {
        "monto": monto,
        "orden_compra": orden_compra,
        "token_ws": token_ws,
    }
