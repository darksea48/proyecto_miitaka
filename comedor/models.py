from django.db import models
from django.contrib.auth.models import User
from cocina.models import CategoriaItem, Item

# Create your models here.

class Mesa(models.Model):
    """Modelo para representar las mesas del restaurante"""
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('ocupada', 'Ocupada'),
        ('reservada', 'Reservada'),
        ('mantenimiento', 'Mantenimiento'),
    ]
    
    UBICACION_CHOICES = [
        ('salon_principal', 'Salón Principal'),
        ('terraza', 'Terraza'),
        ('vip', 'VIP'),
        ('barra', 'Barra'),
    ]
    
    numero = models.PositiveIntegerField(unique=True, verbose_name='Número de Mesa')
    capacidad = models.PositiveIntegerField(verbose_name='Capacidad (personas)')
    ubicacion = models.CharField(max_length=100, choices=UBICACION_CHOICES, verbose_name='Ubicación')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='disponible', verbose_name='Estado')
    
    class Meta:
        verbose_name = 'Mesa'
        verbose_name_plural = 'Mesas'
        ordering = ['numero']
    
    def __str__(self):
        return f"Mesa {self.numero} - {self.ubicacion} ({self.capacidad} personas)"
    
    def get_reservas_activas_count(self):
        return self.reservas.filter(estado__in=['pendiente', 'confirmada', 'en_curso']).count() # -> SELECT COUNT(*) FROM comedor_reserva WHERE estado IN (...) AND mesa_id = self.id

class Cliente(models.Model):
    """Modelo para representar a los clientes"""
    nombre = models.CharField(max_length=100, verbose_name='Nombre Completo')
    telefono = models.CharField(max_length=15, verbose_name='Teléfono', blank=True, null=True)
    email = models.EmailField(verbose_name='Email', blank=True, null=True)
    observaciones = models.TextField(verbose_name='Observaciones', blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Registro')
    
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} - {self.telefono}"


class Reserva(models.Model):
    """Modelo para gestionar las reservas de mesas"""
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('en_curso', 'En Curso'),
        ('terminada', 'Terminada'),
        ('cancelada', 'Cancelada'),
        ('no_asistio', 'No Asistió'),
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True, related_name='reservas', verbose_name='Cliente')
    mesa = models.ForeignKey(Mesa, on_delete=models.SET_NULL, null=True, blank=True, related_name='reservas', verbose_name='Mesa')
    fecha_reserva = models.DateTimeField(verbose_name='Fecha y Hora de Reserva')
    numero_personas = models.IntegerField(verbose_name='Número de Personas')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente', verbose_name='Estado')
    observaciones = models.TextField(verbose_name='Observaciones', blank=True)
    creada_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Creada por')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')
    
    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['-fecha_reserva']
    
    def __str__(self):
        return f"Reserva Mesa {self.mesa.numero} - {self.cliente.nombre} ({self.fecha_reserva.strftime('%d/%m/%Y %H:%M')})"
    
    def save(self, *args, **kwargs):
        """Actualiza el estado de la mesa al guardar la reserva"""
        # Si es una reserva nueva o se está confirmando
        if self.estado in ['pendiente', 'confirmada'] and self.mesa:
            self.mesa.estado = 'reservada'
            self.mesa.save()
        # Si se cancela o termina, verificar si hay otras reservas activas para esa mesa
        elif self.estado in ['cancelada', 'terminada', 'no_asistio'] and self.mesa:
            # Verificar si hay otras reservas activas para esta mesa
            reservas_activas = Reserva.objects.filter(
                mesa=self.mesa,
                estado__in=['pendiente', 'confirmada', 'en_curso']
            ).exclude(id=self.id).exists()
            
            if not reservas_activas:
                self.mesa.estado = 'disponible'
                self.mesa.save()
        
        super().save(*args, **kwargs)
    
    def cancel(self):
        """Cancela la reserva y actualiza el estado de la mesa si es necesario"""
        self.estado = 'cancelada'
        self.save()
        # Actualizar el estado de la mesa si es necesario
        reservas_activas = Reserva.objects.filter( # SELECT COUNT(*) FROM comedor_reserva
            mesa=self.mesa,
            estado__in=['pendiente', 'confirmada', 'en_curso']
        ).exclude(id=self.id).exists()
        
        if not reservas_activas:
            self.mesa.estado = 'disponible'
            self.mesa.save()


class Pedido(models.Model):
    """Modelo para gestionar los pedidos"""
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_preparacion', 'En Preparación'),
        ('listo', 'Listo'),
        ('servido', 'Servido'),
        ('pagado', 'Pagado'),
        ('cancelado', 'Cancelado'),
    ]
    
    TIPO_CHOICES = [
        ('comedor', 'Comedor'),
        ('llevar', 'Para Llevar'),
        ('delivery', 'Delivery'),
    ]
    
    mesa = models.ForeignKey(Mesa, on_delete=models.SET_NULL, null=True, blank=True, related_name='pedidos', verbose_name='Mesa')
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True, related_name='pedidos', verbose_name='Cliente')
    tipo_pedido = models.CharField(max_length=20, choices=TIPO_CHOICES, default='comedor', verbose_name='Tipo de Pedido')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente', verbose_name='Estado')
    observaciones = models.TextField(verbose_name='Observaciones', blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Total')
    atendido_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Atendido por')
    fecha_pedido = models.DateTimeField(auto_now_add=True, verbose_name='Fecha del Pedido')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')
    
    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-fecha_pedido']
    
    def __str__(self):
        mesa_info = f"Mesa {self.mesa.numero}" if self.mesa else "Sin mesa"
        return f"Pedido #{self.id} - {mesa_info} ({self.estado})"
    
    def calcular_total(self):
        """Calcula el total del pedido sumando todos los detalles"""
        total = sum([detalle.subtotal for detalle in self.detalles.all()])
        self.total = total
        self.save()
        return total
    
    def agregar_item(self, item, cantidad=1, observaciones=''):
        """Agrega un item al pedido"""
        detalle = DetallePedido.objects.create(
            pedido=self,
            item=item,
            cantidad=cantidad,
            precio_unitario=item.precio,
            observaciones=observaciones
        )
        self.calcular_total()
        return detalle
    
    def eliminar_item(self, item):
        """Elimina un item del pedido"""
        detalle = self.detalles.filter(item=item).first()
        if detalle:
            detalle.delete()
            self.calcular_total()
            return True
        return False
    
    def actualizar_item(self, item, cantidad):
        """Actualiza la cantidad de un item en el pedido"""
        detalle = self.detalles.filter(item=item).first()
        if detalle:
            detalle.cantidad = cantidad
            detalle.precio_unitario = item.precio
            detalle.save()
            self.calcular_total()
            return detalle
        return None
    
    def generar_descuento(self, porcentaje):
        """Aplica un descuento al total del pedido"""
        descuento = (self.total * porcentaje) / 100
        self.total -= descuento
        self.save()
        return self.total


class DetallePedido(models.Model):
    """Detalles de cada pedido (items ordenados)"""
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles', verbose_name='Pedido')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name='Item')
    cantidad = models.IntegerField(default=1, verbose_name='Cantidad')
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio Unitario')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Subtotal')
    observaciones = models.TextField(blank=True, verbose_name='Observaciones')
    
    class Meta:
        verbose_name = 'Detalle de Pedido'
        verbose_name_plural = 'Detalles de Pedidos'
    
    def save(self, *args, **kwargs):
        """Calcula el subtotal antes de guardar"""
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)
        # Actualizar el total del pedido
        self.pedido.calcular_total()
    
    def __str__(self):
        return f"{self.cantidad}x {self.item.nombre} - ${self.subtotal}"
