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


class MesaCreateView(CreateView):
    model = Mesa
    form_class = MesaForm
    template_name = 'form_mesa.html'
    success_url = reverse_lazy('listar_mesas')
    
    def form_valid(self, form):
        messages.success(self.request, 'Mesa creada exitosamente.')
        return super().form_valid(form)


class MesaUpdateView(UpdateView):
    model = Mesa
    form_class = MesaForm
    template_name = 'form_mesa.html'
    success_url = reverse_lazy('listar_mesas')
    
    def form_valid(self, form):
        messages.success(self.request, 'Mesa actualizada exitosamente.')
        return super().form_valid(form)


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

def reservar_mesa(request, pk):
    
    mesa = get_object_or_404(Mesa, pk=pk) # -> SELECT * FROM comedor_mesa WHERE id = pk LIMIT 1
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        # Hacer el campo mesa no requerido para que no falle la validación
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.mesa = mesa
            # reserva.creada_por = request.user
            reserva.save()
            messages.success(request, 'Mesa reservada exitosamente.')
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


class ClienteCreateView(CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'form_cliente.html'
    success_url = reverse_lazy('listar_clientes')
    
    def form_valid(self, form):
        messages.success(self.request, 'Cliente registrado exitosamente.')
        return super().form_valid(form)


class ClienteUpdateView(UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'form_cliente.html'
    success_url = reverse_lazy('listar_clientes')
    
    def form_valid(self, form):
        messages.success(self.request, 'Cliente actualizado exitosamente.')
        return super().form_valid(form)


def cliente_delete(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk) # -> SELECT * FROM comedor_cliente WHERE id = pk LIMIT 1
    cliente.delete() # -> DELETE FROM comedor_cliente WHERE id = pk
    messages.success(request, 'Cliente eliminado exitosamente.')
    return redirect('listar_clientes')

def crear_reserva_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk) # -> SELECT * FROM comedor_cliente WHERE id = pk LIMIT 1
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        # Hacer el campo cliente no requerido para que no falle la validación
        form.fields['cliente'].required = False
        
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.cliente = cliente
            # reserva.creada_por = request.user
            reserva.save() # -> INSERT INTO comedor_reserva (...) VALUES (...)
            messages.success(request, 'Reserva creada exitosamente para el cliente.')
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
        # TODO: Optimizar con select_related('mesa', 'cliente', 'creada_por')
        # -> SELECT * FROM comedor_reserva ORDER BY fecha_reserva DESC
        queryset = super().get_queryset()
        estado = self.request.GET.get('estado')
        if estado and estado != 'todas':
            # SELECT * FROM comedor_reserva WHERE estado = %s ORDER BY fecha_reserva DESC
            queryset = queryset.filter(estado=estado)
        return queryset 


class ReservaDetailView(DetailView):
    model = Reserva
    template_name = 'detail_reserva.html'
    context_object_name = 'reserva'


class ReservaCreateView(CreateView):
    model = Reserva
    form_class = ReservaForm
    template_name = 'form_reserva.html'
    success_url = reverse_lazy('listar_reservas')
    
    def form_valid(self, form):
        form.instance.creada_por = self.request.user
        messages.success(self.request, 'Reserva creada exitosamente.')
        return super().form_valid(form)


class ReservaUpdateView(UpdateView):
    model = Reserva
    form_class = ReservaForm
    template_name = 'form_reserva.html'
    success_url = reverse_lazy('listar_reservas')
    
    def form_valid(self, form):
        messages.success(self.request, 'Reserva actualizada exitosamente.')
        return super().form_valid(form)


def reserva_delete(request, pk):
    # SELECT * FROM comedor_reserva WHERE id = pk LIMIT 1
    reserva = get_object_or_404(Reserva, pk=pk)
    # DELETE FROM comedor_reserva WHERE id = pk
    reserva.delete()
    messages.success(request, 'Reserva eliminada exitosamente.')
    return redirect('listar_reservas')

def confirmar_reserva(request, pk):
    # SELECT * FROM comedor_reserva WHERE id = pk LIMIT 1
    reserva = get_object_or_404(Reserva, pk=pk)
    reserva.estado = 'confirmada'
    # UPDATE comedor_reserva SET estado = 'confirmada' WHERE id = pk
    reserva.save()
    messages.success(request, 'Reserva confirmada exitosamente.')
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
        # SELECT * FROM comedor_pedido ORDER BY fecha_pedido DESC LIMIT 20
        # TODO: Optimizar con select_related('reserva__mesa', 'reserva__cliente', 'atendido_por')
        queryset = super().get_queryset()
        estado = self.request.GET.get('estado')
        if estado and estado != 'todos':
            # SELECT * FROM comedor_pedido WHERE estado = %s ORDER BY fecha_pedido DESC LIMIT 20
            queryset = queryset.filter(estado=estado)
        return queryset


class PedidoDetailView(DetailView):
    model = Pedido
    template_name = 'detail_pedido.html'
    context_object_name = 'pedido'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # SELECT * FROM comedor_detallepedido WHERE pedido_id = pedido.id
        # TODO: Optimizar con prefetch_related('detalles__item')
        context['detalles'] = self.object.detalles.all()
        return context


class PedidoCreateView(CreateView):
    model = Pedido
    form_class = PedidoForm
    template_name = 'form_pedido.html'
    success_url = reverse_lazy('listar_pedidos')
    
    def form_valid(self, form):
        form.instance.atendido_por = self.request.user
        messages.success(self.request, 'Pedido creado exitosamente.')
        return super().form_valid(form)


class PedidoUpdateView(UpdateView):
    model = Pedido
    form_class = PedidoForm
    template_name = 'form_pedido.html'
    success_url = reverse_lazy('listar_pedidos')
    
    def form_valid(self, form):
        messages.success(self.request, 'Pedido actualizado exitosamente.')
        return super().form_valid(form)


def pedido_delete(request, pk):
    # SELECT * FROM comedor_pedido WHERE id = pk LIMIT 1
    pedido = get_object_or_404(Pedido, pk=pk)
    # DELETE FROM comedor_pedido WHERE id = pk (CASCADE eliminará detalles)
    pedido.delete()
    messages.success(request, 'Pedido eliminado exitosamente.')
    return redirect('listar_pedidos')