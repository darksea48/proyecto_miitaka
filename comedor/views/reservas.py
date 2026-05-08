from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib import messages
from django.urls import reverse_lazy
from ..models import Mesa, Reserva
from ..forms import ReservaForm


class ReservaListView(LoginRequiredMixin, ListView):
    model = Reserva
    template_name = 'list_reservas.html'
    context_object_name = 'reservas'
    paginate_by = 20

    def get_queryset(self):
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


class ReservaDetailView(LoginRequiredMixin, DetailView):
    model = Reserva
    template_name = 'detail_reserva.html'
    context_object_name = 'reserva'


class ReservaCreateView(LoginRequiredMixin, CreateView):
    model = Reserva
    form_class = ReservaForm
    template_name = 'form_reserva.html'
    success_url = reverse_lazy('comedor:listar_reservas')

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
    success_url = reverse_lazy('comedor:listar_reservas')

    def form_valid(self, form):
        messages.success(self.request, 'Reserva actualizada exitosamente.')
        return super().form_valid(form)


@login_required
def reserva_cancel(request, pk):
    # SELECT * FROM comedor_reserva WHERE id = pk LIMIT 1
    reserva = get_object_or_404(Reserva, pk=pk)
    mesa = reserva.mesa

    reserva.cancel()  # Actualiza estado de la reserva y posiblemente el de la mesa
    messages.success(request, f'Reserva cancelada exitosamente. Mesa {mesa.numero} ahora está disponible si no tiene otras reservas activas.')

    return redirect('comedor:listar_reservas')


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

    return redirect('comedor:listar_reservas')


@login_required
def confirmar_reserva(request, pk):
    # SELECT * FROM comedor_reserva WHERE id = pk LIMIT 1
    reserva = get_object_or_404(Reserva, pk=pk)
    reserva.estado = 'confirmada'
    # UPDATE comedor_reserva SET estado = 'confirmada' WHERE id = pk
    # El método save() del modelo actualizará automáticamente el estado de la mesa
    reserva.save()
    messages.success(request, f'Reserva confirmada exitosamente. Mesa {reserva.mesa.numero} está reservada.')
    return redirect('comedor:listar_reservas')
