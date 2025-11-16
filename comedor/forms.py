from django import forms
from django.contrib.auth.models import User
from .models import *
from cocina.models import *


class MesaForm(forms.ModelForm):
    """Formulario para crear y editar mesas"""
    
    UBICACIONES = [
        ('salon_principal', 'Salón Principal'),
        ('terraza', 'Terraza'),
        ('vip', 'VIP'),
        ('barra', 'Barra'),
    ]
    
    ubicacion = forms.ChoiceField(
        choices=UBICACIONES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'placeholder': 'Seleccione la ubicación de la mesa'
        })
    )
    
    class Meta:
        model = Mesa
        fields = ['numero', 'capacidad', 'ubicacion']
        widgets = {
            'numero': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 1, 2, 3...',
                'min': '1'
            }),
            'capacidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 2, 4, 6...',
                'min': '1',
                'max': '20'
            })
        }


class ClienteForm(forms.ModelForm):
    """Formulario para registrar y editar clientes"""
    class Meta:
        model = Cliente
        fields = ['nombre', 'telefono', 'email', 'observaciones']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo del cliente'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+56 9 1234 5678',
                'required': False
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com',
                'required': False
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Alergias, preferencias especiales, etc.',
                'required': False
            })
        }


class ReservaForm(forms.ModelForm):
    """Formulario para crear y gestionar reservas"""
    class Meta:
        model = Reserva
        fields = ['cliente', 'mesa', 'fecha_reserva', 'numero_personas', 'observaciones']
        widgets = {
            'cliente': forms.Select(attrs={
                'class': 'form-select'
            }),
            'mesa': forms.Select(attrs={
                'class': 'form-select'
            }),
            'fecha_reserva': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }, format='%Y-%m-%dT%H:%M'),
            'numero_personas': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '20'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas adicionales sobre la reserva'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configurar el formato de fecha
        self.fields['fecha_reserva'].input_formats = ['%Y-%m-%dT%H:%M']
    
    def clean(self):
        """Validaciones personalizadas del formulario"""
        cleaned_data = super().clean()
        mesa = cleaned_data.get('mesa')
        numero_personas = cleaned_data.get('numero_personas')
        fecha_reserva = cleaned_data.get('fecha_reserva')
        
        # Validar que el número de personas no exceda la capacidad de la mesa
        if mesa and numero_personas:
            if numero_personas > mesa.capacidad:
                # Equivalente a verificar constraint en DB sin hacer INSERT
                self.add_error('numero_personas', 
                    f'La mesa {mesa.numero} tiene capacidad para {mesa.capacidad} personas. '
                    f'No puede reservar para {numero_personas} personas.'
                )
        
        # Validar que la fecha de reserva no sea en el pasado
        if fecha_reserva:
            from django.utils import timezone
            if fecha_reserva < timezone.now():
                # Validación de lógica de negocio
                self.add_error('fecha_reserva', 
                    'La fecha y hora de la reserva no pueden ser en el pasado.'
                )
        
        # Validación de reservas duplicadas (dentro de 2 horas)
        if mesa and fecha_reserva and not self.add_error:
            from datetime import timedelta
            
            # Buscar reservas en rango de ±2 horas
            inicio_rango = fecha_reserva - timedelta(hours=2)
            fin_rango = fecha_reserva + timedelta(hours=2)
            
            reservas_conflicto = Reserva.objects.filter(
                mesa=mesa,
                fecha_reserva__range=[inicio_rango, fin_rango],
                estado__in=['pendiente', 'confirmada', 'en_curso']
            )
            
            # Excluir la reserva actual si estamos editando
            if self.instance.pk:
                reservas_conflicto = reservas_conflicto.exclude(pk=self.instance.pk)
            
            if reservas_conflicto.exists():
                reserva_existente = reservas_conflicto.first()
                self.add_error('fecha_reserva',
                    f'Ya existe una reserva para la mesa {mesa.numero} '
                    f'cerca de esta hora ({reserva_existente.fecha_reserva.strftime("%d/%m/%Y %H:%M")}). '
                    f'Por favor, elija otro horario.'
                )
        
        return cleaned_data


class PedidoForm(forms.ModelForm):
    """Formulario para crear y gestionar pedidos"""
    class Meta:
        model = Pedido
        fields = ['mesa', 'cliente', 'tipo_pedido', 'estado', 'observaciones']
        widgets = {
            'mesa': forms.Select(attrs={
                'class': 'form-select'
            }),
            'cliente': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tipo_pedido': forms.Select(attrs={
                'class': 'form-select'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas adicionales sobre el pedido'
            })
        }


class DetallePedidoForm(forms.ModelForm):
    """Formulario para agregar items a un pedido"""
    class Meta:
        model = DetallePedido
        fields = ['item', 'cantidad', 'observaciones']
        widgets = {
            'item': forms.Select(attrs={
                'class': 'form-select'
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'value': '1'
            }),
            'observaciones': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Sin sal, término medio, sin hielo, etc.'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # SELECT * FROM cocina_item WHERE disponible = 1
        # Filtrar solo items disponibles
        self.fields['item'].queryset = Item.objects.filter(disponible=True)


