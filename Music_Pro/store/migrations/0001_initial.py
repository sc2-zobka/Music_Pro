# Generated by Django 3.2.3 on 2021-07-01 02:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(help_text='Campo requerido y único', max_length=200, unique=True, verbose_name='Nombre de Categoría')),
                ('is_active', models.BooleanField(default=True)),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='store.categoria')),
            ],
            options={
                'verbose_name': 'Categoría',
                'verbose_name_plural': 'Categorias',
            },
        ),
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200, null=True)),
                ('email', models.CharField(max_length=200)),
                ('cliente', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Cliente',
                'verbose_name_plural': 'Clientes',
            },
        ),
        migrations.CreateModel(
            name='Contacto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
                ('apellido', models.CharField(max_length=50, null=True)),
                ('telefono', models.IntegerField()),
                ('email', models.EmailField(help_text='Correo Obligatorio', max_length=254)),
                ('mensaje', models.TextField()),
            ],
            options={
                'verbose_name': 'Contacto',
                'verbose_name_plural': 'Contacto',
            },
        ),
        migrations.CreateModel(
            name='Orden',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_orden', models.DateTimeField(auto_now_add=True)),
                ('es_completa', models.BooleanField(default=False, help_text='indica si la orden está completada o no', verbose_name='completada')),
                ('es_aceptada', models.BooleanField(default=False, help_text='indica si la orden está aceptada por bodega', verbose_name='aceptada')),
                ('transaction_id', models.CharField(max_length=100, null=True)),
                ('retiro_en_tienda', models.BooleanField(default=False, help_text='¿Pedido para despacho?')),
                ('cliente', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='store.cliente')),
            ],
            options={
                'verbose_name': 'Orden',
                'verbose_name_plural': 'Ordenes',
            },
        ),
        migrations.CreateModel(
            name='Tienda',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(help_text='Requerido', max_length=100, verbose_name='Tienda')),
                ('direccion', models.CharField(help_text=' Direccion de tienda solicitante', max_length=200, verbose_name='Direccion')),
                ('ciudad', models.CharField(max_length=200)),
                ('comuna', models.CharField(max_length=200)),
                ('region', models.CharField(max_length=200)),
                ('zipcode', models.CharField(max_length=200)),
            ],
            options={
                'verbose_name': 'Tienda',
                'verbose_name_plural': 'Tiendas',
            },
        ),
        migrations.CreateModel(
            name='Producto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(help_text='Requerido', max_length=255, verbose_name='nombre')),
                ('descripcion', models.TextField(blank=True, help_text='No requerido', verbose_name='descripción')),
                ('precio', models.IntegerField(verbose_name='precio regular')),
                ('es_activo', models.BooleanField(default=True, help_text='Desactiva producto de ser necesario', verbose_name='Producto activo')),
                ('es_oferta', models.BooleanField(default=False, verbose_name='Producto en oferta')),
                ('es_nuevo', models.BooleanField(default=False, verbose_name='Producto nuevo')),
                ('stock', models.PositiveIntegerField(default=0)),
                ('codigo_producto', models.CharField(help_text='Requerido', max_length=50, verbose_name='Codigo de producto')),
                ('sku', models.CharField(help_text='Requerido', max_length=50, verbose_name='SKU')),
                ('imagen', models.ImageField(blank=True, null=True, upload_to='producto')),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='store.categoria')),
                ('tienda', models.ManyToManyField(to='store.Tienda')),
            ],
            options={
                'verbose_name': 'Producto',
                'verbose_name_plural': 'Productos',
            },
        ),
        migrations.CreateModel(
            name='PedidoCasaCentral',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_de_orden', models.DateTimeField(auto_now_add=True)),
                ('es_entregado', models.BooleanField(default=False)),
                ('responsable', models.CharField(help_text='requerido', max_length=100, verbose_name='solicitante de pedido')),
                ('cantidad', models.PositiveIntegerField()),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='store.producto')),
                ('tienda', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='store.tienda')),
            ],
            options={
                'verbose_name': 'Pedido Casa Central',
                'verbose_name_plural': 'Pedidos Casa Central',
            },
        ),
        migrations.CreateModel(
            name='OrdenItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.IntegerField(blank=True, default=0, null=True)),
                ('fecha_agregado', models.DateTimeField(auto_now_add=True)),
                ('orden', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='store.orden')),
                ('producto', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='store.producto')),
            ],
            options={
                'verbose_name': 'Orden Item',
                'verbose_name_plural': 'Orden Item',
            },
        ),
        migrations.CreateModel(
            name='OrdenDeDespacho',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('direccion', models.CharField(max_length=200)),
                ('ciudad', models.CharField(max_length=200)),
                ('comuna', models.CharField(max_length=200)),
                ('region', models.CharField(max_length=200)),
                ('zipcode', models.CharField(max_length=200)),
                ('fecha_agregado', models.DateTimeField(auto_now_add=True)),
                ('cliente', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='store.cliente')),
                ('orden', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='store.orden')),
            ],
        ),
    ]
