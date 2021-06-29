from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from .models import Cliente, Contacto, PedidoCasaCentral, User


class ContactoForms(forms.ModelForm):
    """
    Contacto form
    """

    nombre = forms.CharField(
        required=True,
        min_length=3,
        max_length=50,
        widget=forms.TextInput(
            attrs={"class": "form-control", "pattern": "[A-Za-z ]+", "title": "Debe contener solo letras!"}
        ),
    )

    apellido = forms.CharField(
        required=True,
        min_length=3,
        max_length=50,
        widget=forms.TextInput(
            attrs={"class": "form-control", "pattern": "[A-Za-z ]+", "title": "Debe contener solo letras!"}
        ),
    )

    mensaje = forms.CharField(
        required=True,
        min_length=10,
        max_length=200,
        widget=forms.Textarea(
            attrs={"placeholder": "Maximo 200 caracteres", "title": "Consulte por nuestros productos"}
        ),
    )

    class Meta:
        model = Contacto
        fields = "__all__"


class CustomUserCreationForm(UserCreationForm):
    nombre = forms.CharField(
        required=True,
        min_length=3,
        max_length=80,
        widget=forms.TextInput(
            attrs={"class": "form-control", "pattern": "[A-Za-z ]+", "title": "Debe contener solo letras!"}
        ),
    )

    email = forms.EmailField(required=True)

    def clean_email(self):
        email = self.cleaned_data.get("email")
        mensaje = str()

        try:
            User.objects.get(email=email)
            mensaje = "Correo ya se encuentra en uso."

            validate_email(email)
        except User.DoesNotExist:
            return email
        except ValidationError:
            return email

        raise forms.ValidationError(mensaje)

    class Meta:
        model = User
        fields = ["nombre", "email", "username", "password1", "password2"]


class ModificarClienteForms(forms.ModelForm):
    nombre = forms.CharField(required=True, min_length=3, max_length=120)
    email = forms.EmailField(required=True)
    nombre_usuario = forms.CharField(required=True, min_length=3, max_length=120)

    class Meta:
        model = Cliente
        fields = ["nombre", "email"]


class PedidoCasaCentralForms(forms.ModelForm):
    class Meta:
        model = PedidoCasaCentral
        fields = ["producto", "tienda", "responsable", "cantidad"]


# class OrdenPedidoForms(forms.ModelForm):
#     # nombre = forms.CharField(required=True, min_length=3, max_length=120)
#     # precio = forms.IntegerField(required=True, min_value=1)
#     # imagen = forms.ImageField(required=False)
#     # descripcion = forms.CharField(required=False, min_length=3, max_length=200)
#     # stock = forms.IntegerField(required=True, min_value=0)
#     # #
#     # fecha_orden = forms.DateTimeField()
#     # es_completa = forms.BooleanField(
#     #     label="completada",
#     # )
#     # es_aceptada = forms.BooleanField(
#     #     label="aceptada",
#     # )
#     # transaction_id = forms.CharField(max_length=100, null=True)
#     # retiro_en_tienda = forms.BooleanField(help_text="¿Pedido para despacho?", default=False)

#     class Meta:
#         model = Orden
#         fields = "__all__"
#         exclude = ["transaction_id"]

# class ClientePedidoForms(forms.ModelForm):
#     # nombre = forms.CharField(required=True, min_length=3, max_length=120)
#     # precio = forms.IntegerField(required=True, min_value=1)
#     # imagen = forms.ImageField(required=False)
#     # descripcion = forms.CharField(required=False, min_length=3, max_length=200)
#     # stock = forms.IntegerField(required=True, min_value=0)
#     # #
#     # fecha_orden = forms.DateTimeField()
#     # es_completa = forms.BooleanField(
#     #     label="completada",
#     # )
#     # es_aceptada = forms.BooleanField(
#     #     label="aceptada",
#     # )
#     # transaction_id = forms.CharField(max_length=100, null=True)
#     # retiro_en_tienda = forms.BooleanField(help_text="¿Pedido para despacho?", default=False)

#     class Meta:
#         model = Cliente
#         fields = "__all__"
