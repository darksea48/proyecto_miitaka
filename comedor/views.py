from django.forms import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Mesa, Cliente, Reserva, Pedido, DetallePedido
from .forms import MesaForm, ClienteForm, ReservaForm, PedidoForm, DetallePedidoForm

# Create your views here.

# ============================================
# VISTA PRINCIPAL DE COMEDOR
# ============================================

class ComedorIndexView(TemplateView):
    template_name = 'index_comedor.html'


# ============================================
# VISTAS PARA MESAS
# ============================================

class MesaListView(ListView):
    model = Mesa
    template_name = 'list.html'
    context_object_name = 'mesas'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Gestión de Mesas'
        context['tipo_vista'] = 'mesas'
        context['url_crear'] = reverse_lazy('crear_mesa')
        context['texto_boton_crear'] = 'Nueva Mesa'
        return context
    
    def get_queryset(self):
        # SELECT * FROM comedor_mesa ORDER BY numero
        queryset = super().get_queryset()
        estado = self.request.GET.get('estado')
        if estado and estado != 'todas':
            # SELECT * FROM comedor_mesa WHERE estado = %s ORDER BY numero
            queryset = queryset.filter(estado=estado)
        return queryset


class MesaCreateView(LoginRequiredMixin, CreateView):
    model = Mesa
    form_class = MesaForm
    template_name = 'form_mesa.html'
    success_url = reverse_lazy('listar_mesas')
    
    def form_valid(self, form):
        messages.success(self.request, 'Mesa creada exitosamente.')
        return super().form_valid(form)


class MesaUpdateView(LoginRequiredMixin, UpdateView):
    model = Mesa
    form_class = MesaForm
    template_name = 'form_mesa.html'
    success_url = reverse_lazy('listar_mesas')
    
    def form_valid(self, form):
        messages.success(self.request, 'Mesa actualizada exitosamente.')
        return super().form_valid(form)

@login_required
def liberar_mesa(request, pk):
    mesa = get_object_or_404(Mesa, pk=pk) # -> SELECT * FROM comedor_mesa WHERE id = pk LIMIT 1
    
    if mesa.estado != 'ocupada':
        messages.error(request, f'La mesa {mesa.numero} no está ocupada. Estado actual: {mesa.get_estado_display()}')
        return redirect('listar_mesas')
    
    # Cambiar el estado de la mesa a disponible
    mesa.estado = 'disponible'
    mesa.save() # -> UPDATE comedor_mesa SET estado = 'disponible' WHERE id = pk
    
    messages.success(request, f'Mesa {mesa.numero} liberada exitosamente. Ahora está disponible.')
    return redirect('listar_mesas')

@login_required
def mesa_delete(request, pk):
    # SELECT * FROM comedor_mesa WHERE id = pk LIMIT 1
    mesa = get_object_or_404(Mesa, pk=pk)
    # DELETE FROM comedor_mesa WHERE id = pk
    mesa.delete()
    messages.success(request, 'Mesa eliminada exitosamente.')
    return redirect('listar_mesas')

class MesaDetailView(DetailView):
    model = Mesa
    template_name = 'detail_mesa.html'
    context_object_name = 'mesa'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Buscar la reserva activa asociada a la mesa
        reserva_activa = Reserva.objects.filter(
            mesa=self.object,
            estado__in=['pendiente', 'confirmada', 'en_curso']
        ).first()
        
        # Buscar si hay un pedido activo para esta mesa
        pedido_activo = Pedido.objects.filter(
            mesa=self.object,
            estado__in=['pendiente', 'en_preparacion', 'listo', 'servido']
        ).first()
        
        context['reserva_activa'] = reserva_activa
        context['pedido_activo'] = pedido_activo
        return context

@login_required
def reservar_mesa(request, pk):
    
    mesa = get_object_or_404(Mesa, pk=pk) # -> SELECT * FROM comedor_mesa WHERE id = pk LIMIT 1
    
    # Verificar si la mesa está disponible
    if mesa.estado in ['ocupada', 'mantenimiento']:
        messages.error(request, f'La mesa no está disponible. Estado actual: {mesa.get_estado_display()}')
        return redirect('listar_mesas')
    
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        # Hacer el campo mesa no requerido para que no falle la validación
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.mesa = mesa
            reserva.creada_por = request.user
            reserva.save()  # Esto automáticamente cambiará el estado de la mesa a 'reservada'
            messages.success(request, f'Mesa {mesa.numero} reservada exitosamente. Estado actualizado a: Reservada')
            return redirect('listar_mesas')
        else:
            messages.error(request, 'Por favor, corrige los errores del formulario.')
            form = ReservaForm(initial={'mesa': mesa})
            form.fields['mesa'].widget.attrs['disabled'] = True
            form.fields['mesa'].required = False
            return render(request, 'form_reserva.html', {'form': form, 'mesa': mesa})
    else:
        form = ReservaForm(initial={'mesa': mesa})
        form.fields['mesa'].widget.attrs['disabled'] = True
        form.fields['mesa'].required = False
    return render(request, 'form_reserva.html', {'form': form, 'mesa': mesa})

@login_required
def recepcionar_mesa(request, pk):
    mesa = get_object_or_404(Mesa, pk=pk) # -> SELECT * FROM comedor_mesa WHERE id = pk LIMIT 1
    
    if mesa.estado != 'reservada':
        messages.error(request, f'La mesa {mesa.numero} no está reservada. Estado actual: {mesa.get_estado_display()}')
        return redirect('listar_mesas')
    
    # Buscar la reserva activa (confirmada o pendiente) asociada a la mesa
    reserva = Reserva.objects.filter(
        mesa=mesa, 
        estado__in=['pendiente', 'confirmada']
    ).first() # -> SELECT * FROM comedor_reserva WHERE mesa_id = mesa.id AND estado IN ('pendiente', 'confirmada') ORDER BY fecha_reserva LIMIT 1
    
    if not reserva:
        messages.error(request, f'No se encontró una reserva activa para la mesa {mesa.numero}.')
        return redirect('listar_mesas')
    
    # Cambiar el estado de la mesa a ocupada
    mesa.estado = 'ocupada'
    mesa.save() # -> UPDATE comedor_mesa SET estado = 'ocupada' WHERE id = pk
    
    # Cambiar el estado de la reserva a en_curso
    reserva.estado = 'en_curso'
    reserva.save() # -> UPDATE comedor_reserva SET estado = 'en_curso' WHERE id = reserva.id
    
    messages.success(request, f'Mesa {mesa.numero} recepcionada exitosamente. Cliente: {reserva.cliente.nombre}. Ahora está ocupada.')
    return redirect('listar_mesas')

# ============================================
# VISTAS PARA CLIENTES
# ============================================

class ClienteListView(ListView):
    model = Cliente
    template_name = 'list.html'
    context_object_name = 'clientes'
    paginate_by = 20
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Gestión de Clientes'
        context['tipo_vista'] = 'clientes'
        context['url_crear'] = reverse_lazy('crear_cliente')
        context['texto_boton_crear'] = 'Nuevo Cliente'
        return context
    
    def get_queryset(self):
        queryset = super().get_queryset() # -> SELECT * FROM comedor_cliente ORDER BY id DESC
        buscar = self.request.GET.get('q')
        if buscar:
            queryset = queryset.filter(
                Q(nombre__icontains=buscar) | 
                Q(telefono__icontains=buscar) | 
                Q(email__icontains=buscar)
            ) # -> SELECT * FROM comedor_cliente WHERE nombre LIKE %q% OR telefono LIKE %q% OR email LIKE %q%
        return queryset


class ClienteDetailView(DetailView):
    model = Cliente
    template_name = 'detail_cliente.html'
    context_object_name = 'cliente'


class ClienteCreateView(LoginRequiredMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'form_cliente.html'
    success_url = reverse_lazy('listar_clientes')
    
    def form_valid(self, form):
        messages.success(self.request, 'Cliente registrado exitosamente.')
        return super().form_valid(form)


class ClienteUpdateView(LoginRequiredMixin, UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'form_cliente.html'
    success_url = reverse_lazy('listar_clientes')
    
    def form_valid(self, form):
        messages.success(self.request, 'Cliente actualizado exitosamente.')
        return super().form_valid(form)


@login_required
def cliente_delete(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk) # -> SELECT * FROM comedor_cliente WHERE id = pk LIMIT 1
    cliente.delete() # -> DELETE FROM comedor_cliente WHERE id = pk
    messages.success(request, 'Cliente eliminado exitosamente.')
    return redirect('listar_clientes')

@login_required
def crear_reserva_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk) # -> SELECT * FROM comedor_cliente WHERE id = pk LIMIT 1
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        # Hacer el campo cliente no requerido para que no falle la validación
        form.fields['cliente'].required = False
        
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.cliente = cliente
            mesa = form.cleaned_data.get('mesa')
            
            # Validar disponibilidad de la mesa
            if mesa and mesa.estado in ['ocupada', 'mantenimiento']:
                messages.error(request, f'La mesa {mesa.numero} no está disponible. Estado actual: {mesa.get_estado_display()}')
                form = ReservaForm(initial={'cliente': cliente})
                form.fields['cliente'].widget.attrs['disabled'] = True
                form.fields['cliente'].required = False
                return render(request, 'form_reserva.html', {'form': form, 'cliente': cliente})
            
            reserva.creada_por = request.user
            reserva.save() # -> INSERT INTO comedor_reserva (...) VALUES (...) y actualiza estado de mesa
            messages.success(request, f'Reserva creada exitosamente para el cliente. Mesa {mesa.numero} reservada.')
            return redirect('ver_cliente', pk=cliente.pk)
        else:
            messages.error(request, 'Por favor, corrige los errores del formulario.')
            form = ReservaForm(initial={'cliente': cliente})
            form.fields['cliente'].widget.attrs['disabled'] = True
            form.fields['cliente'].required = False
            return render(request, 'form_reserva.html', {'form': form, 'cliente': cliente})
    else:
        form = ReservaForm(initial={'cliente': cliente})
        form.fields['cliente'].widget.attrs['disabled'] = True
        form.fields['cliente'].required = False
    return render(request, 'form_reserva.html', {'form': form, 'cliente': cliente})

# ============================================
# VISTAS PARA RESERVAS
# ============================================

class ReservaListView(ListView):
    model = Reserva
    template_name = 'list.html'
    context_object_name = 'reservas'
    paginate_by = 20
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Gestión de Reservas'
        context['tipo_vista'] = 'reservas'
        context['url_crear'] = reverse_lazy('crear_reserva')
        context['texto_boton_crear'] = 'Nueva Reserva'
        return context
    
    def get_queryset(self):
        # Optimización con select_related para evitar múltiples consultas
        # SELECT * FROM comedor_reserva 
        # INNER JOIN comedor_mesa ON (comedor_reserva.mesa_id = comedor_mesa.id)
        # INNER JOIN comedor_cliente ON (comedor_reserva.cliente_id = comedor_cliente.id)
        # INNER JOIN auth_user ON (comedor_reserva.creada_por_id = auth_user.id)
        # ORDER BY fecha_reserva DESC
        queryset = Reserva.objects.select_related('mesa', 'cliente', 'creada_por').all()
        estado = self.request.GET.get('estado')
        if estado and estado != 'todas':
            # SELECT * FROM comedor_reserva WHERE estado = %s ORDER BY fecha_reserva DESC
            queryset = queryset.filter(estado=estado)
        return queryset 


class ReservaDetailView(DetailView):
    model = Reserva
    template_name = 'detail_reserva.html'
    context_object_name = 'reserva'


class ReservaCreateView(LoginRequiredMixin, CreateView):
    model = Reserva
    form_class = ReservaForm
    template_name = 'form_reserva.html'
    success_url = reverse_lazy('listar_reservas')
    
    def form_valid(self, form):
        form.instance.creada_por = self.request.user
        mesa = form.cleaned_data.get('mesa')
        
        # Validar que la mesa esté disponible
        if mesa and mesa.estado in ['ocupada', 'mantenimiento']:
            messages.error(self.request, f'La mesa {mesa.numero} no está disponible. Estado actual: {mesa.get_estado_display()}')
            return self.form_invalid(form)
        
        response = super().form_valid(form)
        messages.success(self.request, f'Reserva creada exitosamente. Mesa {mesa.numero} actualizada a estado: Reservada')
        return response


class ReservaUpdateView(LoginRequiredMixin, UpdateView):
    model = Reserva
    form_class = ReservaForm
    template_name = 'form_reserva.html'
    success_url = reverse_lazy('listar_reservas')
    
    def form_valid(self, form):
        messages.success(self.request, 'Reserva actualizada exitosamente.')
        return super().form_valid(form)

@login_required
def reserva_cancel(request, pk):
    # SELECT * FROM comedor_reserva WHERE id = pk LIMIT 1
    reserva = get_object_or_404(Reserva, pk=pk)
    mesa = reserva.mesa
    
    reserva.cancel() # Esto actualizará el estado de la reserva y posiblemente el estado de la mesa, lógica realizada en el modelo
    messages.success(request, f'Reserva cancelada exitosamente. Mesa {mesa.numero} ahora está disponible si no tiene otras reservas activas.')
    
    return redirect('listar_reservas')

@login_required
def reserva_delete(request, pk):
    # SELECT * FROM comedor_reserva WHERE id = pk LIMIT 1
    reserva = get_object_or_404(Reserva, pk=pk)
    mesa = reserva.mesa
    
    # Verificar si hay otras reservas activas para esta mesa
    reservas_activas = Reserva.objects.filter(
        mesa=mesa,
        estado__in=['pendiente', 'confirmada', 'en_curso']
    ).exclude(id=reserva.id).exists()

    # DELETE FROM comedor_reserva WHERE id = pk
    reserva.delete()
    
    # Si no hay más reservas activas, liberar la mesa
    if not reservas_activas:
        mesa.estado = 'disponible'
        mesa.save()
        messages.success(request, f'Reserva eliminada exitosamente. Mesa {mesa.numero} ahora está disponible.')
    else:
        messages.success(request, 'Reserva eliminada exitosamente.')
    
    return redirect('listar_reservas')

@login_required
def confirmar_reserva(request, pk):
    # SELECT * FROM comedor_reserva WHERE id = pk LIMIT 1
    reserva = get_object_or_404(Reserva, pk=pk)
    reserva.estado = 'confirmada'
    # UPDATE comedor_reserva SET estado = 'confirmada' WHERE id = pk
    # El método save() del modelo actualizará automáticamente el estado de la mesa
    reserva.save()
    messages.success(request, f'Reserva confirmada exitosamente. Mesa {reserva.mesa.numero} está reservada.')
    return redirect('listar_reservas')


# ============================================
# VISTAS PARA PEDIDOS
# ============================================

class PedidoListView(ListView):
    model = Pedido
    template_name = 'list.html'
    context_object_name = 'pedidos'
    paginate_by = 20
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Gestión de Pedidos'
        context['tipo_vista'] = 'pedidos'
        context['url_crear'] = reverse_lazy('crear_pedido')
        context['texto_boton_crear'] = 'Nuevo Pedido'
        return context
    
    def get_queryset(self):
        # Optimización con select_related para evitar múltiples consultas
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


class PedidoDetailView(DetailView):
    model = Pedido
    template_name = 'detail_pedido.html'
    context_object_name = 'pedido'
    
    def get_queryset(self):
        # Optimización con select_related y prefetch_related
        # SELECT * FROM comedor_pedido WHERE id = %s
        # INNER JOIN comedor_mesa ON (comedor_pedido.mesa_id = comedor_mesa.id)
        # INNER JOIN comedor_cliente ON (comedor_pedido.cliente_id = comedor_cliente.id)
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
    success_url = reverse_lazy('listar_pedidos')
    
    def form_valid(self, form):
        form.instance.atendido_por = self.request.user
        messages.success(self.request, 'Pedido creado exitosamente.')
        return super().form_valid(form)

class PedidoUpdateView(LoginRequiredMixin, UpdateView):
    model = Pedido
    form_class = PedidoForm
    template_name = 'form_pedido.html'
    success_url = reverse_lazy('listar_pedidos')
    
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
    return redirect('listar_pedidos')

@login_required
def crear_pedido_mesa(request, mesa_id):
    mesa = get_object_or_404(Mesa, pk=mesa_id)  # -> SELECT * FROM comedor_mesa WHERE id = mesa_id LIMIT 1
    
    # Buscar la reserva en curso asociada a la mesa
    reserva = Reserva.objects.filter(
        mesa=mesa, 
        estado='en_curso'
    ).first() # -> SELECT * FROM comedor_reserva WHERE mesa_id = mesa_id AND estado = 'en_curso' ORDER BY fecha_reserva LIMIT 1
    
    if not reserva:
        messages.error(request, f'No se encontró una reserva en curso para la mesa {mesa.numero}. Debe recepcionar la mesa primero.')
        return redirect('listar_mesas')
    
    cliente = reserva.cliente  # Obtener el cliente de la reserva
    
    # Buscar si ya existe un pedido activo para esta mesa
    pedido_existente = Pedido.objects.filter(
        mesa=mesa,
        estado__in=['pendiente', 'en_preparacion', 'listo', 'servido']
    ).first() # -> SELECT * FROM comedor_pedido WHERE mesa_id = mesa_id AND estado IN (...) ORDER BY fecha_pedido DESC LIMIT 1
    
    if request.method == 'POST':
        if pedido_existente:
            # Editar el pedido existente
            form = PedidoForm(request.POST, instance=pedido_existente)
        else:
            # Crear un nuevo pedido
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
            
            return redirect('ver_pedido', pk=pedido.pk)
        else:
            messages.error(request, 'Por favor, corrige los errores del formulario.')
    else:
        if pedido_existente:
            # Cargar el pedido existente en el formulario
            form = PedidoForm(instance=pedido_existente)
            messages.info(request, f'Editando pedido existente #{pedido_existente.id} para esta mesa.')
        else:
            # Crear un formulario nuevo
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
        'object': pedido_existente  # Para que el template sepa si está editando
    })

# ============================================
# VISTAS PARA ITEMS DE PEDIDOS
# ============================================

@login_required
def agregar_item_pedido(request, pedido_id):
    """Vista para agregar items a un pedido existente"""
    pedido = get_object_or_404(Pedido, pk=pedido_id)  # -> SELECT * FROM comedor_pedido WHERE id = pedido_id LIMIT 1
    
    if request.method == 'POST':
        form = DetallePedidoForm(request.POST)
        if form.is_valid():
            detalle = form.save(commit=False)
            detalle.pedido = pedido
            detalle.precio_unitario = detalle.item.precio  # Capturar precio actual
            detalle.save()  # -> INSERT INTO comedor_detallepedido
            
            # Recalcular total del pedido
            pedido.calcular_total()
            
            messages.success(request, f'Item "{detalle.item.nombre}" agregado al pedido.')
            return redirect('ver_pedido', pk=pedido.pk)
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
    """Vista para editar un item del pedido"""
    detalle = get_object_or_404(DetallePedido, pk=detalle_id)  # -> SELECT * FROM comedor_detallepedido WHERE id = detalle_id LIMIT 1
    pedido = detalle.pedido
    
    if request.method == 'POST':
        form = DetallePedidoForm(request.POST, instance=detalle)
        if form.is_valid():
            detalle = form.save(commit=False)
            detalle.precio_unitario = detalle.item.precio  # Actualizar precio
            detalle.save()  # -> UPDATE comedor_detallepedido
            
            # Recalcular total del pedido
            pedido.calcular_total()
            
            messages.success(request, f'Item actualizado exitosamente.')
            return redirect('ver_pedido', pk=pedido.pk)
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
    """Vista para eliminar un item del pedido"""
    detalle = get_object_or_404(DetallePedido, pk=detalle_id)  # -> SELECT * FROM comedor_detallepedido WHERE id = detalle_id LIMIT 1
    pedido = detalle.pedido
    
    if request.method == 'POST':
        item_nombre = detalle.item.nombre
        detalle.delete()  # -> DELETE FROM comedor_detallepedido WHERE id = detalle_id
        
        # Recalcular total del pedido
        pedido.calcular_total()
        
        messages.success(request, f'Item "{item_nombre}" eliminado del pedido.')
        return redirect('ver_pedido', pk=pedido.pk)
    
    return render(request, 'confirmar_eliminar_item.html', {
        'detalle': detalle,
        'pedido': pedido
    })