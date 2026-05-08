from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DetailView
from django.contrib import messages
from django.urls import reverse_lazy
from ..models import Mesa, Reserva, Pedido
from ..forms import MesaForm, ReservaForm


class ComedorIndexView(LoginRequiredMixin, TemplateView):
    template_name = 'index_comedor.html'


class MesaListView(LoginRequiredMixin, ListView):
    model = Mesa
    template_name = 'list_mesas.html'
    context_object_name = 'mesas'

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
    success_url = reverse_lazy('comedor:listar_mesas')

    def form_valid(self, form):
        messages.success(self.request, 'Mesa creada exitosamente.')
        return super().form_valid(form)


class MesaUpdateView(LoginRequiredMixin, UpdateView):
    model = Mesa
    form_class = MesaForm
    template_name = 'form_mesa.html'
    success_url = reverse_lazy('comedor:listar_mesas')

    def form_valid(self, form):
        messages.success(self.request, 'Mesa actualizada exitosamente.')
        return super().form_valid(form)


class MesaDetailView(LoginRequiredMixin, DetailView):
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
def liberar_mesa(request, pk):
    mesa = get_object_or_404(Mesa, pk=pk)  # -> SELECT * FROM comedor_mesa WHERE id = pk LIMIT 1

    if mesa.estado != 'ocupada':
        messages.error(request, f'La mesa {mesa.numero} no está ocupada. Estado actual: {mesa.get_estado_display()}')
        return redirect('comedor:listar_mesas')

    # Cambiar el estado de la mesa a disponible
    mesa.estado = 'disponible'
    mesa.save()  # -> UPDATE comedor_mesa SET estado = 'disponible' WHERE id = pk

    messages.success(request, f'Mesa {mesa.numero} liberada exitosamente. Ahora está disponible.')
    return redirect('comedor:listar_mesas')


@login_required
def mesa_delete(request, pk):
    # SELECT * FROM comedor_mesa WHERE id = pk LIMIT 1
    mesa = get_object_or_404(Mesa, pk=pk)
    # DELETE FROM comedor_mesa WHERE id = pk
    mesa.delete()
    messages.success(request, 'Mesa eliminada exitosamente.')
    return redirect('comedor:listar_mesas')


@login_required
def reservar_mesa(request, pk):
    mesa = get_object_or_404(Mesa, pk=pk)  # -> SELECT * FROM comedor_mesa WHERE id = pk LIMIT 1

    # Verificar si la mesa está disponible
    if mesa.estado in ['ocupada', 'mantenimiento']:
        messages.error(request, f'La mesa no está disponible. Estado actual: {mesa.get_estado_display()}')
        return redirect('comedor:listar_mesas')

    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.mesa = mesa
            reserva.creada_por = request.user
            reserva.save()  # Automáticamente cambia el estado de la mesa a 'reservada'
            messages.success(request, f'Mesa {mesa.numero} reservada exitosamente. Estado actualizado a: Reservada')
            return redirect('comedor:listar_mesas')
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
    mesa = get_object_or_404(Mesa, pk=pk)  # -> SELECT * FROM comedor_mesa WHERE id = pk LIMIT 1

    if mesa.estado != 'reservada':
        messages.error(request, f'La mesa {mesa.numero} no está reservada. Estado actual: {mesa.get_estado_display()}')
        return redirect('comedor:listar_mesas')

    # Buscar la reserva activa (confirmada o pendiente) asociada a la mesa
    # SELECT * FROM comedor_reserva WHERE mesa_id = mesa.id AND estado IN ('pendiente', 'confirmada') LIMIT 1
    reserva = Reserva.objects.filter(
        mesa=mesa,
        estado__in=['pendiente', 'confirmada']
    ).first()

    if not reserva:
        messages.error(request, f'No se encontró una reserva activa para la mesa {mesa.numero}.')
        return redirect('comedor:listar_mesas')

    # Cambiar el estado de la mesa a ocupada
    mesa.estado = 'ocupada'
    mesa.save()  # -> UPDATE comedor_mesa SET estado = 'ocupada' WHERE id = pk

    # Cambiar el estado de la reserva a en_curso
    reserva.estado = 'en_curso'
    reserva.save()  # -> UPDATE comedor_reserva SET estado = 'en_curso' WHERE id = reserva.id

    messages.success(request, f'Mesa {mesa.numero} recepcionada exitosamente. Cliente: {reserva.cliente.nombre}. Ahora está ocupada.')
    return redirect('comedor:listar_mesas')
