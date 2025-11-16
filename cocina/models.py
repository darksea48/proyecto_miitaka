from django.db import models

# Create your models here.

class CategoriaItem(models.Model):
    """Categorías de items del menú (platos, bebidas, cocteles, etc.)"""
    nombre = models.CharField(max_length=100, unique=True, verbose_name='Nombre')
    descripcion = models.TextField(verbose_name='Descripción', blank=True)
    lugar_item = models.CharField(max_length=100, choices=[('bar', 'Bar'), ('cocina', 'Cocina')], verbose_name='Proveniencia del Item', default='cocina')
    
    class Meta:
        verbose_name = 'Categoría de Item'
        verbose_name_plural = 'Categorías de Items'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Item(models.Model):
    """Modelo para los items del menú (platos, bebidas, cocteles, mocktails, etc.)"""
    nombre = models.CharField(max_length=200, verbose_name='Nombre del Item')
    descripcion = models.TextField(verbose_name='Descripción')
    categoria = models.ForeignKey(CategoriaItem, on_delete=models.SET_NULL, null=True, related_name='items', verbose_name='Categoría')
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio')
    disponible = models.BooleanField(default=True, verbose_name='Disponible')
    tiempo_preparacion = models.IntegerField(verbose_name='Tiempo de Preparación (minutos)', default=15)
    
    class Meta:
        verbose_name = 'Item'
        verbose_name_plural = 'Items'
        ordering = ['categoria', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} - ${self.precio}"

