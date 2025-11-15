from django.contrib import admin
from .models import CategoriaItem, Item


# ============================================
# ADMIN CLASSES
# ============================================

@admin.register(CategoriaItem)
class CategoriaItemAdmin(admin.ModelAdmin):
    """Administración de Categorías de Items"""
    list_display = ['nombre', 'descripcion_corta', 'total_items']
    search_fields = ['nombre', 'descripcion']
    ordering = ['nombre']
    
    def descripcion_corta(self, obj):
        """Muestra una versión corta de la descripción"""
        if obj.descripcion:
            return obj.descripcion[:50] + '...' if len(obj.descripcion) > 50 else obj.descripcion
        return '-'
    descripcion_corta.short_description = 'Descripción'
    
    def total_items(self, obj):
        """Cuenta el total de items en la categoría"""
        return obj.items.count()
    total_items.short_description = 'Items'


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    """Administración de Items del Menú"""
    list_display = ['nombre', 'categoria', 'precio', 'disponible', 'tiempo_preparacion', 'disponibilidad_badge']
    list_filter = ['disponible', 'categoria', 'tiempo_preparacion']
    search_fields = ['nombre', 'descripcion']
    ordering = ['categoria', 'nombre']
    list_per_page = 20
    list_editable = ['precio', 'disponible']
    
    fieldsets = (
        ('Información del Item', {
            'fields': ('nombre', 'descripcion', 'categoria')
        }),
        ('Detalles', {
            'fields': ('precio', 'tiempo_preparacion', 'disponible')
        }),
    )
    
    def disponibilidad_badge(self, obj):
        """Muestra la disponibilidad con color"""
        if obj.disponible:
            return '<span style="color: green; font-weight: bold;">✓ Disponible</span>'
        return '<span style="color: red; font-weight: bold;">✗ No Disponible</span>'
    disponibilidad_badge.short_description = 'Disponibilidad'
    disponibilidad_badge.allow_tags = True
