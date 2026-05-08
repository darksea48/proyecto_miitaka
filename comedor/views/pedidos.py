from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib import messages
from django.urls import reverse_lazy
from ..models import Mesa, Reserva, Pedido, DetallePedido
from ..forms import PedidoForm, DetallePedidoForm


class PedidoListView(LoginRequiredMixin, ListView):
    model = Pedido
    template_name = 'list_pedidos.html'
    context_object_name = 'pedidos'
    paginate_by = 20

    def get_queryset(self):
        # SELECT * FROM comedor_pedido
        # INNER JOIN comedor_mesa ON (comedor_pedido.mesa_id = comedor_mesa.id)
        # INNER JOIN comedor_cliente ON (comedor_pedido.cliente_id = comedor_cliente.id)
        # INNER JOIN auth_user ON (comedor_pedido.atendido_por_id = auth_user.id)
        # ORDER BY fecha_pedido DESC LIMIT 20
        queryset = Pedido.objects.select_related('mesa', 'cliente', 'atendido_por').all()
        estado = self.request.GET.get('estado')
        if estado and estado != 'todos':
            # SELECT * FROM comedor_pedido WHERE estado = %s ORDER BY fecha_pedido DESC LIMIT 20
            queryset = queryset.filter(estado=estado)
        return queryset


class PedidoDetailView(LoginRequiredMixin, DetailView):
    model = Pedido
    template_name = 'detail_pedido.html'
    context_object_name = 'pedido'

    def get_queryset(self):
        # SELECT * FROM comedor_pedido WHERE id = %s
        # INNER JOIN comedor_mesa, comedor_cliente, auth_user
        # + SELECT * FROM comedor_detallepedido WHERE pedido_id IN (...)
        # + SELECT * FROM cocina_item WHERE id IN (...)
        return Pedido.objects.select_related('mesa', 'cliente', 'atendido_por').prefetch_related('detalles__item')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ya optimizado con prefetch_related en get_queryset
        context['detalles'] = self.object.detalles.all()
        return context


class PedidoCreateView(LoginRequiredMixin, CreateView):
    model = Pedido
    form_class = PedidoForm
    template_name = 'form_pedido.html'
    success_url = reverse_lazy('comedor:listar_pedidos')

    def form_valid(self, form):
        form.instance.atendido_por = self.request.user
        messages.success(self.request, 'Pedido creado exitosamente.')
        return super().form_valid(form)


class PedidoUpdateView(LoginRequiredMixin, UpdateView):
    model = Pedido
    form_class = PedidoForm
    template_name = 'form_pedido.html'
    success_url = reverse_lazy('comedor:listar_pedidos')

    def form_valid(self, form):
        messages.success(self.request, 'Pedido actualizado exitosamente.')
        return super().form_valid(form)


@login_required
def pedido_delete(request, pk):
    # SELECT * FROM comedor_pedido WHERE id = pk LIMIT 1
    pedido = get_object_or_404(Pedido, pk=pk)
    # DELETE FROM comedor_pedido WHERE id = pk (CASCADE eliminará detalles)
    pedido.delete()
    messages.success(request, 'Pedido eliminado exitosamente.')
    return redirect('comedor:listar_pedidos')


@login_required
def crear_pedido_mesa(request, mesa_id):
    mesa = get_object_or_404(Mesa, pk=mesa_id)  # -> SELECT * FROM comedor_mesa WHERE id = mesa_id LIMIT 1

    # Buscar la reserva en curso asociada a la mesa
    # SELECT * FROM comedor_reserva WHERE mesa_id = mesa_id AND estado = 'en_curso' LIMIT 1
    reserva = Reserva.objects.filter(
        mesa=mesa,
        estado='en_curso'
    ).first()

    if not reserva:
        messages.error(request, f'No se encontró una reserva en curso para la mesa {mesa.numero}. Debe recepcionar la mesa primero.')
        return redirect('comedor:listar_mesas')

    cliente = reserva.cliente  # Obtener el cliente de la reserva

    # Buscar si ya existe un pedido activo para esta mesa
    # SELECT * FROM comedor_pedido WHERE mesa_id = mesa_id AND estado IN (...) LIMIT 1
    pedido_existente = Pedido.objects.filter(
        mesa=mesa,
        estado__in=['pendiente', 'en_preparacion', 'listo', 'servido']
    ).first()

    if request.method == 'POST':
        if pedido_existente:
            form = PedidoForm(request.POST, instance=pedido_existente)
        else:
            form = PedidoForm(request.POST)

        if form.is_valid():
            pedido = form.save(commit=False)
            pedido.mesa = mesa
            pedido.cliente = cliente
            pedido.atendido_por = request.user
            pedido.save()  # -> INSERT/UPDATE comedor_pedido

            if pedido_existente:
                messages.success(request, f'Pedido actualizado exitosamente para la Mesa {mesa.numero} - Cliente: {cliente.nombre}.')
            else:
                messages.success(request, f'Pedido creado exitosamente para la Mesa {mesa.numero} - Cliente: {cliente.nombre}.')

            return redirect('comedor:ver_pedido', pk=pedido.pk)
        else:
            messages.error(request, 'Por favor, corrige los errores del formulario.')
    else:
        if pedido_existente:
            form = PedidoForm(instance=pedido_existente)
            messages.info(request, f'Editando pedido existente #{pedido_existente.id} para esta mesa.')
        else:
            form = PedidoForm(initial={'mesa': mesa, 'cliente': cliente})

        form.fields['mesa'].widget.attrs['disabled'] = True
        form.fields['mesa'].required = False
        form.fields['cliente'].widget.attrs['disabled'] = True
        form.fields['cliente'].required = False

    return render(request, 'form_pedido.html', {
        'form': form,
        'mesa': mesa,
        'cliente': cliente,
        'reserva': reserva,
        'object': pedido_existente
    })


@login_required
def agregar_item_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)  # -> SELECT * FROM comedor_pedido WHERE id = pedido_id LIMIT 1

    if request.method == 'POST':
        form = DetallePedidoForm(request.POST)
        if form.is_valid():
            detalle = form.save(commit=False)
            detalle.pedido = pedido
            detalle.precio_unitario = detalle.item.precio  # Capturar precio actual del item
            detalle.save()  # -> INSERT INTO comedor_detallepedido

            # Recalcular total del pedido
            pedido.calcular_total()

            messages.success(request, f'Item "{detalle.item.nombre}" agregado al pedido.')
            return redirect('comedor:ver_pedido', pk=pedido.pk)
        else:
            messages.error(request, 'Por favor, corrige los errores del formulario.')
    else:
        form = DetallePedidoForm()

    return render(request, 'agregar_item_pedido.html', {
        'form': form,
        'pedido': pedido
    })


@login_required
def editar_item_pedido(request, detalle_id):
    detalle = get_object_or_404(DetallePedido, pk=detalle_id)  # -> SELECT * FROM comedor_detallepedido WHERE id = detalle_id LIMIT 1
    pedido = detalle.pedido

    if request.method == 'POST':
        form = DetallePedidoForm(request.POST, instance=detalle)
        if form.is_valid():
            detalle = form.save(commit=False)
            detalle.precio_unitario = detalle.item.precio  # Actualizar precio al vigente
            detalle.save()  # -> UPDATE comedor_detallepedido

            # Recalcular total del pedido
            pedido.calcular_total()

            messages.success(request, 'Item actualizado exitosamente.')
            return redirect('comedor:ver_pedido', pk=pedido.pk)
        else:
            messages.error(request, 'Por favor, corrige los errores del formulario.')
    else:
        form = DetallePedidoForm(instance=detalle)

    return render(request, 'agregar_item_pedido.html', {
        'form': form,
        'pedido': pedido,
        'detalle': detalle
    })


@login_required
def eliminar_item_pedido(request, detalle_id):
    detalle = get_object_or_404(DetallePedido, pk=detalle_id)  # -> SELECT * FROM comedor_detallepedido WHERE id = detalle_id LIMIT 1
    pedido = detalle.pedido

    item_nombre = detalle.item.nombre
    detalle.delete()  # -> DELETE FROM comedor_detallepedido WHERE id = detalle_id

    # Recalcular total del pedido
    pedido.calcular_total()

    messages.success(request, f'Item "{item_nombre}" eliminado del pedido.')
    return redirect('comedor:ver_pedido', pk=pedido.pk)
