from django.contrib import admin
from .models import Mesa, Cliente, Reserva, Pedido, DetallePedido


# ============================================
# INLINE ADMIN CLASSES
# ============================================

class DetallePedidoInline(admin.TabularInline):
    """Inline para mostrar detalles de pedidos dentro del pedido"""
    model = DetallePedido
    extra = 1
    fields = ['item', 'cantidad', 'precio_unitario', 'subtotal', 'observaciones']
    readonly_fields = ['subtotal']


# ============================================
# ADMIN CLASSES
# ============================================

@admin.register(Mesa)
class MesaAdmin(admin.ModelAdmin):
    """Administración de Mesas"""
    list_display = ['numero', 'capacidad', 'ubicacion', 'estado', 'estado_badge']
    list_filter = ['estado', 'ubicacion', 'capacidad']
    search_fields = ['numero', 'ubicacion']
    ordering = ['numero']
    list_per_page = 20
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('numero', 'capacidad', 'ubicacion')
        }),
        ('Estado', {
            'fields': ('estado',)
        }),
    )
    
    def estado_badge(self, obj):
        """Muestra el estado con color"""
        colors = {
            'disponible': 'green',
            'ocupada': 'red',
            'reservada': 'orange',
            'mantenimiento': 'gray'
        }
        color = colors.get(obj.estado, 'black')
        return f'<span style="color: {color}; font-weight: bold;">●</span> {obj.get_estado_display()}'
    estado_badge.short_description = 'Estado Visual'
    estado_badge.allow_tags = True


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    """Administración de Clientes"""
    list_display = ['nombre', 'telefono', 'email', 'fecha_registro', 'total_reservas', 'total_pedidos']
    list_filter = ['fecha_registro']
    search_fields = ['nombre', 'telefono', 'email']
    ordering = ['-fecha_registro']
    list_per_page = 20
    readonly_fields = ['fecha_registro']
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'telefono', 'email')
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
        ('Sistema', {
            'fields': ('fecha_registro',),
            'classes': ('collapse',)
        }),
    )
    
    def total_reservas(self, obj):
        """Cuenta el total de reservas del Cliente"""
        return obj.reservas.count()
    total_reservas.short_description = 'Reservas'
    
    def total_pedidos(self, obj):
        """Cuenta el total de pedidos del Cliente"""
        return obj.pedidos.count()
    total_pedidos.short_description = 'Pedidos'


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    """Administración de Reservas"""
    list_display = ['id', 'cliente', 'mesa', 'fecha_reserva', 'numero_personas', 'estado', 'creada_por']
    list_filter = ['estado', 'fecha_reserva', 'mesa']
    search_fields = ['cliente__nombre', 'cliente__telefono', 'mesa__numero']
    ordering = ['-fecha_reserva']
    list_per_page = 20
    readonly_fields = ['creada_por', 'fecha_creacion', 'fecha_actualizacion']
    date_hierarchy = 'fecha_reserva'
    
    fieldsets = (
        ('Información de Reserva', {
            'fields': ('cliente', 'mesa', 'fecha_reserva', 'numero_personas')
        }),
        ('Estado y Observaciones', {
            'fields': ('estado', 'observaciones')
        }),
        ('Información del Sistema', {
            'fields': ('creada_por', 'fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Asigna automáticamente el usuario que crea la reserva"""
        if not change:  # Solo cuando se crea
            obj.creada_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    """Administración de Pedidos"""
    list_display = ['id', 'mesa', 'cliente', 'estado', 'total', 'fecha_pedido', 'atendido_por']
    list_filter = ['estado', 'fecha_pedido']
    search_fields = ['id', 'cliente__nombre', 'mesa__numero']
    ordering = ['-fecha_pedido']
    list_per_page = 20
    readonly_fields = ['total', 'atendido_por', 'fecha_pedido', 'fecha_actualizacion']
    date_hierarchy = 'fecha_pedido'
    inlines = [DetallePedidoInline]
    
    fieldsets = (
        ('Información del Pedido', {
            'fields': ('mesa', 'cliente', 'estado')
        }),
        ('Detalles', {
            'fields': ('observaciones', 'total')
        }),
        ('Información del Sistema', {
            'fields': ('atendido_por', 'fecha_pedido', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Asigna automáticamente el usuario que crea el pedido"""
        if not change:  # Solo cuando se crea
            obj.atendido_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    """Administración de Detalles de Pedidos"""
    list_display = ['pedido', 'item', 'cantidad', 'precio_unitario', 'subtotal', 'observaciones']
    list_filter = ['pedido__fecha_pedido', 'item']
    search_fields = ['pedido__id', 'item__nombre']
    ordering = ['-pedido__fecha_pedido']
    readonly_fields = ['subtotal']
    
    fieldsets = (
        ('Pedido', {
            'fields': ('pedido',)
        }),
        ('Item', {
            'fields': ('item', 'cantidad', 'precio_unitario', 'subtotal')
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
    )

