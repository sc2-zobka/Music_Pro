from rest_framework import viewsets

from .models import OrdenPedido, Producto
from .serializers import OrdenPedidoSerializer, ProductoSerializer


class ProductoViewset(viewsets.ModelViewSet):

    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    http_method_names = ["get"]

    def get_queryset(self):
        productos = Producto.objects.all()
        codigo_producto = self.request.GET.get("codigo_producto")

        if codigo_producto:
            productos = productos.filter(codigo_producto=codigo_producto)

        return productos


class OrdenPedidoViewSet(viewsets.ModelViewSet):

    queryset = OrdenPedido.objects.all()
    serializer_class = OrdenPedidoSerializer
    http_method_names = ["get", "post"]
