from rest_framework import serializers

from .models import Categoria, OrdenPedido, Producto, Tienda


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["nombre_categoria", "id"]


class ProductoSerializer(serializers.ModelSerializer):

    # categoria = serializers.CharField(read_only=True, source="categoria.nombre_categoria")
    categoria = CategoriaSerializer(read_only=True)
    # categoria_id = serializers.PrimaryKeyRelatedField(queryset=Categoria.objects.all(), source="categoria")

    class Meta:
        model = Producto
        fields = "__all__"


class TiendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tienda
        fields = "__all__"


class OrdenPedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrdenPedido
        fields = "__all__"
