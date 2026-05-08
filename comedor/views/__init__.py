from .mesas import (
    ComedorIndexView,
    MesaListView, MesaCreateView, MesaUpdateView, MesaDetailView,
    liberar_mesa, mesa_delete, reservar_mesa, recepcionar_mesa,
)
from .clientes import (
    ClienteListView, ClienteCreateView, ClienteUpdateView, ClienteDetailView,
    cliente_delete, crear_reserva_cliente,
)
from .reservas import (
    ReservaListView, ReservaCreateView, ReservaUpdateView, ReservaDetailView,
    reserva_cancel, reserva_delete, confirmar_reserva,
)
from .pedidos import (
    PedidoListView, PedidoCreateView, PedidoUpdateView, PedidoDetailView,
    pedido_delete, crear_pedido_mesa,
    agregar_item_pedido, editar_item_pedido, eliminar_item_pedido,
)
