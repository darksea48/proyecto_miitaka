from datetime import timedelta

from django import forms
from django.utils import timezone

from utils import BootstrapFormMixin
from .models import Mesa, Cliente, Reserva, Pedido, DetallePedido
from cocina.models import Item


class MesaForm(BootstrapFormMixin, forms.ModelForm):
    UBICACIONES = [
        ('salon_principal', 'Salón Principal'),
        ('terraza', 'Terraza'),
        ('vip', 'VIP'),
        ('barra', 'Barra'),
    ]

    ubicacion = forms.ChoiceField(
        choices=UBICACIONES,
        widget=forms.Select(attrs={'placeholder': 'Seleccione la ubicación de la mesa'})
    )

    class Meta:
        model = Mesa
        fields = ['numero', 'capacidad', 'ubicacion']
        widgets = {
            'numero': forms.NumberInput(attrs={'placeholder': 'Ej: 1, 2, 3...', 'min': '1'}),
            'capacidad': forms.NumberInput(attrs={'placeholder': 'Ej: 2, 4, 6...', 'min': '1', 'max': '20'}),
        }


class ClienteForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'telefono', 'email', 'observaciones']
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Nombre completo del cliente'}),
            'telefono': forms.TextInput(attrs={'placeholder': '+56 9 1234 5678'}),
            'email': forms.EmailInput(attrs={'placeholder': 'correo@ejemplo.com'}),
            'observaciones': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Alergias, preferencias especiales, etc.'}),
        }


class ReservaForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['cliente', 'mesa', 'fecha_reserva', 'numero_personas', 'observaciones']
        widgets = {
            'cliente': forms.Select(),
            'mesa': forms.Select(),
            'fecha_reserva': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'numero_personas': forms.NumberInput(attrs={'min': '1', 'max': '20'}),
            'observaciones': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Notas adicionales sobre la reserva'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha_reserva'].input_formats = ['%Y-%m-%dT%H:%M']

    def clean(self):
        cleaned_data = super().clean()
        mesa = cleaned_data.get('mesa')
        numero_personas = cleaned_data.get('numero_personas')
        fecha_reserva = cleaned_data.get('fecha_reserva')

        if mesa and numero_personas and numero_personas > mesa.capacidad:
            self.add_error('numero_personas',
                f'La mesa {mesa.numero} tiene capacidad para {mesa.capacidad} personas. '
                f'No puede reservar para {numero_personas} personas.'
            )

        if fecha_reserva and fecha_reserva < timezone.now():
            self.add_error('fecha_reserva',
                'La fecha y hora de la reserva no pueden ser en el pasado.'
            )

        if mesa and fecha_reserva:
            self._validar_sin_conflictos(mesa, fecha_reserva)

        return cleaned_data

    def _validar_sin_conflictos(self, mesa, fecha_reserva):
        inicio_rango = fecha_reserva - timedelta(hours=2)
        fin_rango = fecha_reserva + timedelta(hours=2)

        reservas_conflicto = Reserva.objects.filter(
            mesa=mesa,
            fecha_reserva__range=[inicio_rango, fin_rango],
            estado__in=['pendiente', 'confirmada', 'en_curso']
        )

        if self.instance.pk:
            reservas_conflicto = reservas_conflicto.exclude(pk=self.instance.pk)

        if reservas_conflicto.exists():
            reserva_existente = reservas_conflicto.first()
            self.add_error('fecha_reserva',
                f'Ya existe una reserva para la mesa {mesa.numero} '
                f'cerca de esta hora ({reserva_existente.fecha_reserva.strftime("%d/%m/%Y %H:%M")}). '
                f'Por favor, elija otro horario.'
            )


class PedidoForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['mesa', 'cliente', 'tipo_pedido', 'estado', 'observaciones']
        widgets = {
            'mesa': forms.Select(),
            'cliente': forms.Select(),
            'tipo_pedido': forms.Select(),
            'estado': forms.Select(),
            'observaciones': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Notas adicionales sobre el pedido'}),
        }


class DetallePedidoForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = DetallePedido
        fields = ['item', 'cantidad', 'observaciones']
        widgets = {
            'item': forms.Select(),
            'cantidad': forms.NumberInput(attrs={'min': '1', 'value': '1'}),
            'observaciones': forms.TextInput(attrs={'placeholder': 'Ej: Sin sal, término medio, sin hielo, etc.'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # SELECT * FROM cocina_item WHERE disponible = 1
        self.fields['item'].queryset = Item.objects.filter(disponible=True)
