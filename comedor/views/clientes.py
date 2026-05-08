from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from ..models import Cliente
from ..forms import ClienteForm, ReservaForm


class ClienteListView(LoginRequiredMixin, ListView):
    model = Cliente
    template_name = 'list_clientes.html'
    context_object_name = 'clientes'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()  # -> SELECT * FROM comedor_cliente ORDER BY nombre
        buscar = self.request.GET.get('q')
        if buscar:
            # SELECT * FROM comedor_cliente WHERE nombre LIKE %q% OR telefono LIKE %q% OR email LIKE %q%
            queryset = queryset.filter(
                Q(nombre__icontains=buscar) |
                Q(telefono__icontains=buscar) |
                Q(email__icontains=buscar)
            )
        return queryset


class ClienteDetailView(LoginRequiredMixin, DetailView):
    model = Cliente
    template_name = 'detail_cliente.html'
    context_object_name = 'cliente'


class ClienteCreateView(LoginRequiredMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'form_cliente.html'
    success_url = reverse_lazy('comedor:listar_clientes')

    def form_valid(self, form):
        messages.success(self.request, 'Cliente registrado exitosamente.')
        return super().form_valid(form)


class ClienteUpdateView(LoginRequiredMixin, UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'form_cliente.html'
    success_url = reverse_lazy('comedor:listar_clientes')

    def form_valid(self, form):
        messages.success(self.request, 'Cliente actualizado exitosamente.')
        return super().form_valid(form)


@login_required
def cliente_delete(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)  # -> SELECT * FROM comedor_cliente WHERE id = pk LIMIT 1
    cliente.delete()  # -> DELETE FROM comedor_cliente WHERE id = pk
    messages.success(request, 'Cliente eliminado exitosamente.')
    return redirect('comedor:listar_clientes')


@login_required
def crear_reserva_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)  # -> SELECT * FROM comedor_cliente WHERE id = pk LIMIT 1
    if request.method == 'POST':
        form = ReservaForm(request.POST)
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
            reserva.save()  # -> INSERT INTO comedor_reserva (...) y actualiza estado de mesa
            messages.success(request, f'Reserva creada exitosamente para el cliente. Mesa {mesa.numero} reservada.')
            return redirect('comedor:ver_cliente', pk=cliente.pk)
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
