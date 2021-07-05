from django.urls import include, path
from rest_framework import routers

from .views import OrdenPedidoViewSet, ProductoViewset

router = routers.DefaultRouter()
router.register("productos", ProductoViewset)
router.register("ordenes-de-pedido", OrdenPedidoViewSet)


urlpatterns = [
    path("api/v1/", include(router.urls)),
]
