from rest_framework import serializers

from .models import PedidoCasaCentral


class PedidoCasaCentralSerializer(serializers.ModelSerializer):
    class Meta:
        model = PedidoCasaCentral  # modelo a Serializar
        fields = "__all__"
