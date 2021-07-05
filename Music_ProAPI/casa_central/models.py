from django.db import models
from django.db.models.fields.related import ForeignKey
from mptt.models import MPTTModel, TreeForeignKey


class Categoria(MPTTModel):

    nombre_categoria = models.CharField(
        max_length=200,
        verbose_name=("Nombre de Categoría"),
        help_text=("Campo requerido y único"),
        unique=True,
    )
    # slug = models.SlugField(max_length=200, unique=True)
    parent = TreeForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")
    is_active = models.BooleanField(default=True)

    class MPTTMeta:
        order_insertion_by = ["nombre_categoria"]

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorias"

    def __str__(self):
        return self.nombre_categoria


class Producto(models.Model):

    categoria = models.ForeignKey(Categoria, on_delete=models.RESTRICT)
    nombre = models.CharField(
        verbose_name=("nombre"),
        help_text=("Requerido"),
        max_length=255,
    )
    stock = models.PositiveIntegerField(
        blank=False,
        default=0,
    )
    codigo_producto = models.CharField(
        verbose_name=("Codigo de producto"),
        help_text=("Requerido"),
        max_length=50,
        blank=False,
        unique=True,
    )
    sku = models.CharField(
        verbose_name=("SKU"),
        help_text=("Requerido"),
        max_length=50,
        blank=False,
        unique=True,
    )
    descripcion = models.TextField(verbose_name=("descripción"), help_text=("Agregar descripción"), blank=True)
    # slug = models.SlugField(max_length=255)
    precio = models.PositiveIntegerField(
        verbose_name="precio",
        blank=False,
    )
    es_activo = models.BooleanField(
        verbose_name=("Producto activo"),
        help_text=("Desactiva producto de ser necesario"),
        default=True,
    )
    fecha_creado = models.DateTimeField(("Creado el"), auto_now_add=True, editable=False)

    class Meta:
        # ordering = ("-created_at",)
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return self.nombre


class Tienda(models.Model):

    # slug = models.SlugField(max_length=255)
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


class OrdenPedido(models.Model):

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
        verbose_name = "Orden de pedido"
        verbose_name_plural = "Ordenes de pedido"

    def __str__(self):
        return str(self.id)
