from django.urls import path
from .views import *

urlpatterns = [   
    # Página principal del comedor
    path('', ComedorIndexView.as_view(), name='comedor_index'),
    
    # URLs para Mesas
    path('mesas/', MesaListView.as_view(), name='listar_mesas'),
    path('mesas/crear/', MesaCreateView.as_view(), name='crear_mesa'),
    path('mesas/<int:pk>/editar/', MesaUpdateView.as_view(), name='editar_mesa'),
    path('mesas/<int:pk>/eliminar/', mesa_delete, name='eliminar_mesa'),
    path('mesas/<int:pk>/', MesaDetailView.as_view(), name='ver_mesa'),
    path('mesas/<int:pk>/reservar/', reservar_mesa, name='reservar_mesa'),
    path('mesas/<int:pk>/liberar/', liberar_mesa, name='liberar_mesa'),
    path('mesas/<int:pk>/recepcionar/', recepcionar_mesa, name='recepcionar_mesa'),
    
    # URLs para Clientes
    path('clientes/', ClienteListView.as_view(), name='listar_clientes'),
    path('clientes/crear/', ClienteCreateView.as_view(), name='crear_cliente'),
    path('clientes/<int:pk>/', ClienteDetailView.as_view(), name='ver_cliente'),
    path('clientes/<int:pk>/editar/', ClienteUpdateView.as_view(), name='editar_cliente'),
    path('clientes/<int:pk>/eliminar/', cliente_delete, name='eliminar_cliente'),
    path('clientes/<int:pk>/reservar/', crear_reserva_cliente, name='crear_reserva_cliente'),
    
    # URLs para Reservas
    path('reservas/', ReservaListView.as_view(), name='listar_reservas'),
    path('reservas/crear/', ReservaCreateView.as_view(), name='crear_reserva'),
    path('reservas/<int:pk>/', ReservaDetailView.as_view(), name='ver_reserva'),
    path('reservas/<int:pk>/editar/', ReservaUpdateView.as_view(), name='editar_reserva'),
    path('reservas/<int:pk>/eliminar/', reserva_delete, name='eliminar_reserva'),
    path('reservas/<int:pk>/confirmar/', confirmar_reserva, name='confirmar_reserva'),
    path('reservas/<int:pk>/cancelar/', reserva_cancel, name='cancelar_reserva'),
    
    # URLs para Pedidos
    path('pedidos/', PedidoListView.as_view(), name='listar_pedidos'),
    path('pedidos/crear/', PedidoCreateView.as_view(), name='crear_pedido'),
    path('pedidos/<int:pk>/', PedidoDetailView.as_view(), name='ver_pedido'),
    path('pedidos/<int:pk>/editar/', PedidoUpdateView.as_view(), name='editar_pedido'),
    path('pedidos/<int:pk>/eliminar/', pedido_delete, name='eliminar_pedido'),
    path('pedidos/crear/<int:mesa_id>/', crear_pedido_mesa, name='crear_pedido_mesa'),
]