from django import forms

from utils import BootstrapFormMixin
from .models import CategoriaItem, Item


class CategoriaItemForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = CategoriaItem
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Ej: Entradas, Platos Fuertes, Bebidas, Cocteles'}),
            'descripcion': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Descripción de la categoría'}),
        }


class ItemForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Item
        fields = ['nombre', 'descripcion', 'categoria', 'precio', 'disponible', 'tiempo_preparacion']
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Nombre del item (plato, bebida, coctel, etc.)'}),
            'descripcion': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Descripción del item'}),
            'categoria': forms.Select(),
            'precio': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'placeholder': '0.00'}),
            'disponible': forms.CheckboxInput(),
            'tiempo_preparacion': forms.NumberInput(attrs={'min': '1', 'placeholder': '15'}),
        }
