from django import forms
from .models import CategoriaItem, Item


class CategoriaItemForm(forms.ModelForm):
    """Formulario para crear y editar categorías de items"""
    class Meta:
        model = CategoriaItem
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Entradas, Platos Fuertes, Bebidas, Cocteles'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción de la categoría'
            })
        }


class ItemForm(forms.ModelForm):
    """Formulario para crear y editar items del menú"""
    class Meta:
        model = Item
        fields = ['nombre', 'descripcion', 'categoria', 'precio', 'disponible', 'tiempo_preparacion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del item (plato, bebida, coctel, etc.)'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del item'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select'
            }),
            'precio': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'disponible': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'tiempo_preparacion': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': '15'
            })
        }
