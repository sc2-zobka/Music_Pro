from django.contrib.auth.models import AbstractUser, User
from django.db import models
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey


class Cliente(models.Model):
    cliente = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200)  # TO-DO: refactor field by fetching email from Django User
    # apellido = models.CharField(max_length=200, null=True)
    # telefono = models.CharField(max_length=9, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = _("Cliente")
        verbose_name_plural = _("Clientes")


class Categoria(MPTTModel):

    nombre = models.CharField(
        max_length=200,
        verbose_name=_("Nombre de Categoría"),
        help_text=_("Campo requerido y único"),
        unique=True,
    )
    parent = TreeForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")
    is_active = models.BooleanField(default=True)

    class MPTTMeta:
        order_insertion_by = ["nombre"]

    class Meta:
        verbose_name = _("Categoría")
        verbose_name_plural = _("Categorias")

    def __str__(self):
        return self.nombre


class Tienda(models.Model):

    nombre = models.CharField(
        verbose_name=("Tienda"),
        help_text=("Requerido"),
        max_length=100,
    )
    direccion = models.CharField(
        verbose_name="Direccion",
        help_text=" Direccion de tienda solicitante",
        max_length=200,
        null=False,
    )
    ciudad = models.CharField(
        max_length=200,
        null=False,
    )
    comuna = models.CharField(max_length=200, null=False)
    region = models.CharField(max_length=200, null=False)
    zipcode = models.CharField(max_length=200)

    class Meta:
        verbose_name = "Tienda"
        verbose_name_plural = "Tiendas"

    def __str__(self):
        return self.nombre


class Producto(models.Model):

    categoria = models.ForeignKey(Categoria, on_delete=models.RESTRICT)
    tienda = models.ManyToManyField(Tienda)
    nombre = models.CharField(
        verbose_name=_("nombre"),
        help_text=_("Requerido"),
        max_length=255,
    )
    descripcion = models.TextField(verbose_name=_("descripción"), help_text=_("No requerido"), blank=True)
    precio = models.IntegerField(verbose_name="precio regular")
    es_activo = models.BooleanField(
        verbose_name=_("Producto activo"),
        help_text=_("Desactiva producto de ser necesario"),
        default=True,
    )
    es_oferta = models.BooleanField(
        verbose_name=_("Producto en oferta"),
        default=False,
    )
    es_nuevo = models.BooleanField(
        verbose_name=_("Producto nuevo"),
        default=False,
    )
    stock = models.PositiveIntegerField(default=0)
    codigo_producto = models.CharField(verbose_name=("Codigo de producto"), help_text=("Requerido"), max_length=50)
    sku = models.CharField(verbose_name=("SKU"), help_text=("Requerido"), max_length=50)
    imagen = models.ImageField(upload_to="producto", null=True, blank=True)

    class Meta:

        verbose_name = _("Producto")
        verbose_name_plural = _("Productos")

    def __str__(self):
        return self.nombre


class Orden(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_orden = models.DateTimeField(auto_now_add=True)
    es_completa = models.BooleanField(
        default=False,
        verbose_name="completada",
        help_text="indica si la orden está completada o no",
    )
    es_aceptada = models.BooleanField(
        default=False,
        verbose_name="aceptada",
        help_text="indica si la orden está aceptada por bodega",
    )
    transaction_id = models.CharField(max_length=100, null=True)
    retiro_en_tienda = models.BooleanField(help_text="¿Pedido para despacho?", default=False)

    def __str__(self):
        return f"Orden de compra #{self.id} asociada a {self.cliente}"

    class Meta:
        verbose_name = "Orden"
        verbose_name_plural = "Ordenes"

    @property
    def get_cart_total(self):
        orden_items = self.ordenitem_set.all()
        total = sum([item.get_total for item in orden_items])
        return total

    @property
    def get_cart_items(self):
        orden_items = self.ordenitem_set.all()
        total = sum([item.cantidad for item in orden_items])
        return total


class OrdenItem(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    orden = models.ForeignKey(Orden, on_delete=models.SET_NULL, null=True)
    cantidad = models.IntegerField(default=0, null=True, blank=True)
    fecha_agregado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Orden Item"
        verbose_name_plural = "Orden Item"

    @property
    def get_total(self):
        total = self.producto.precio * self.cantidad
        return total

    def __str__(self):
        return f"{self.producto.nombre} -> Orden #{self.orden.id}"


class OrdenDeDespacho(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True)
    orden = models.ForeignKey(Orden, on_delete=models.SET_NULL, null=True)
    direccion = models.CharField(max_length=200, null=False)
    ciudad = models.CharField(max_length=200, null=False)
    comuna = models.CharField(max_length=200, null=False)
    region = models.CharField(max_length=200, null=False)
    zipcode = models.CharField(max_length=200, null=False)
    fecha_agregado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Orden despacho #{self.id}"


class Contacto(models.Model):
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50, null=True)
    telefono = models.IntegerField()
    email = models.EmailField(null=False, help_text="Correo Obligatorio")
    mensaje = models.TextField()

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Contacto"
        verbose_name_plural = "Contacto"


class PedidoCasaCentral(models.Model):

    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    tienda = models.ForeignKey(Tienda, on_delete=models.PROTECT)
    fecha_de_orden = models.DateTimeField(auto_now_add=True)
    es_entregado = models.BooleanField(default=False)
    responsable = models.CharField(
        verbose_name="solicitante de pedido",
        help_text="requerido",
        max_length=100,
        blank=False,
    )
    cantidad = models.PositiveIntegerField()

    class Meta:
        verbose_name = "Pedido Casa Central"
        verbose_name_plural = "Pedidos Casa Central"

    def __str__(self):
        return str(self.id)
