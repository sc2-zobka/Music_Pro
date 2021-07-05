import datetime
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
from django.views.decorators.csrf import csrf_exempt
from transbank.webpay.webpay_plus import transaction

from .forms import (
    ContactoForms,
    CustomCambioContrasenaForm,
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

    cart_data = cartData(request)
    cartItems = cart_data["cartItems"]
    orden = cart_data["orden"]
    items = cart_data["items"]

    productos = Producto.objects.all()
    monedas = None

    if not "CURRENCY_CODES" in request.session or len(request.session["CURRENCY_CODES"]) == 0:
        monedas = Moneda.objects.all()

        tmp_json = serializers.serialize("json", monedas)

        request.session["CURRENCY_CODES"] = json.loads(tmp_json)
        print(request.session["CURRENCY_CODES"])

    if "AMT_CONVERSION" in request.session:
        valor_cambio = float(request.session["AMT_CONVERSION"][request.session["CURRENCY_CODE"]])
    print(monedas)
    data = {
        "productos": productos,
        "cartItems": cartItems,
        "monedas": monedas,
        "valor_cambio": valor_cambio,
    }

    return render(request, "store/tienda.html", data)


def carro(request):
    valor_cambio = 1

    cart_data = cartData(request)

    cartItems = cart_data["cartItems"]
    orden = cart_data["orden"]
    items = cart_data["items"]

    if "AMT_CONVERSION" in request.session:
        valor_cambio = float(request.session["AMT_CONVERSION"][request.session["CURRENCY_CODE"]])

    data = {
        "items": items,
        "orden": orden,
        "cartItems": cartItems,
        "valor_cambio": valor_cambio,
    }

    return render(request, "store/carro.html", data)


def checkout(request):
    valor_cambio = 1

    cart_data = cartData(request)

    cartItems = cart_data["cartItems"]
    orden = cart_data["orden"]
    items = cart_data["items"]

    tiendas = Tienda.objects.all()

    if len(items) <= 0:
        messages.warning(request, "Carro de compras vacio, agrege productos")
        return redirect("tienda")

    if "AMT_CONVERSION" in request.session:
        valor_cambio = float(request.session["AMT_CONVERSION"][request.session["CURRENCY_CODE"]])

    data = {
        "items": items,
        "orden": orden,
        "cartItems": cartItems,
        "tiendas": tiendas,
        "valor_cambio": valor_cambio,
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

    if request.method == "POST":
        messages.success(request, "Orden de compra registrada, recuerde enviar la evidencia al correo dado")
        return redirect("tienda")

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
                usuario = User.objects.get(username=request.user.username)
                usuario.username = formulario.cleaned_data["nombre_usuario"]
                usuario.save()
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
            url = "http://localhost:8010/api/v1/productos/?codigo_producto=" + str(codigo_producto)
        else:
            url = "http://localhost:8010/api/v1/productos/"
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


@csrf_exempt
def webpay(request, monto):
    session_id = "sessionId"
    valor_cambio = 1

    if "sessionid" in request.COOKIES:
        session_id = request.COOKIES["sessionid"]

    monto_pagar = float(monto)
    orden_a_compra = datetime.datetime.now().timestamp()

    url_regreso = "http://localhost:8000/retorno_webpay/"

    if "AMT_CONVERSION" in request.session:
        valor_cambio = float(request.session["AMT_CONVERSION"][request.session["CURRENCY_CODE"]])

    response = transaction.Transaction.create(orden_a_compra, session_id, monto_pagar, url_regreso)

    token_ws = response.token
    form = response.url

    data = {
        "monto": monto_pagar,
        "orden_compra": orden_a_compra,
        "token_ws": token_ws,
        "form": form,
        "valor_cambio": valor_cambio,
    }

    return render(request, "store/webpay.html", data)


@csrf_exempt
def retorno_webpay(request):
    token = request.POST["token_ws"]
    resultado = transaction.Transaction.commit(token)
    obtenido = resultado.response_code

    data = {
        "codigo_autorizacion": resultado.buy_order,
        "monto": resultado.amount,
        "codigo_respuesta": obtenido,
        "url_redireccion": "http://localhost:8000/final_webpay/",
        "token_ws": token,
    }

    return render(request, "store/retorno_webpay.html", data)


@csrf_exempt
def final_webpay(request):
    tienda = None
    direccion = None
    comuna = None
    codigo_zip = None
    ciudad = None
    region = None

    valor_cambio = 1

    # Obtener datos de envio
    if "isdespacho" in request.COOKIES:
        if request.COOKIES["isdespacho"] == "1":
            direccion = request.COOKIES["direccion"]
            comuna = request.COOKIES["comuna"]
            codigo_zip = request.COOKIES["zipcode"]
            ciudad = request.COOKIES["ciudad"]
            region = request.COOKIES["region"]
        else:
            tienda = request.COOKIES["tienda"]

        # if request.user.is_authenticated:
        token = request.POST["token_ws"]
        resultado = transaction.Transaction.commit(token)

        # cliente = request.user.cliente
        # orden = Orden.objects.create(cliente=cliente, es_completa=False)
        # orden = Orden()
        # total = resultado.amount
        orden = None

        # PRUEBA
        print(request.user)
        if request.user.is_authenticated:
            cliente = request.user.cliente
            orden, created = Orden.objects.get_or_create(cliente=cliente, es_completa=False)

        else:
            data = {
                "form": {
                    "nombre": request.COOKIES["nombre"],
                    "apellido": request.COOKIES["apellidos"],
                    "email": request.COOKIES["email"],
                    "telefono": request.COOKIES["telefono"],
                    "tienda": tienda,
                }
            }
            # data = {
            #     "nombre": request.COOKIES["nombre"],
            #     "apellidos": request.COOKIES["apellidos"],
            #     "email": request.COOKIES["email"],
            #     "telefono": request.COOKIES["telefono"],
            # }
            # data["form"]["nombre"] = request.COOKIES["nombre"]
            # data["form"]["apellidos"] = request.COOKIES["apellidos"]
            # data["form"]["email"] = request.COOKIES["email"]
            # data["form"]["telefono"] = request.COOKIES["telefono"]
            print("entro")
            cliente, orden = guestOrden(request, data)
        # PRUEBA

        if request.COOKIES["isdespacho"] == "0":
            orden.retiro_en_tienda = True

            tienda = Tienda.objects.get(nombre=tienda)
            orden.tienda = tienda

        orden.transaction_id = resultado.buy_order

        orden.es_completa = True
        orden.save()

        if orden.es_completa == True and orden.retiro_en_tienda == False:
            # create Orden de Despacho instance
            OrdenDeDespacho.objects.create(
                cliente=cliente,
                orden=orden,
                direccion=direccion,
                ciudad=ciudad,
                comuna=comuna,
                region=region,
                zipcode=codigo_zip,
            )

            # else:
            #     print("User is not logged in")

            messages.success(request, "Compra realizada correctamente!")
    else:
        print("no entro")

    return render(request, "store/final_webpay.html")
