from django.test import TestCase, Client as TestClient
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from decimal import Decimal
from .models import Mesa, Cliente, Reserva, Pedido, DetallePedido
from .forms import MesaForm, ClienteForm, ReservaForm, PedidoForm
from cocina.models import CategoriaItem, Item


# ============================================
# TESTS DE MODELOS
# ============================================

class MesaModelTest(TestCase):
    """Tests para el modelo Mesa"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.mesa = Mesa.objects.create(
            numero=1,
            capacidad=4,
            ubicacion='salon_principal'
        )
    
    def test_crear_mesa(self):
        """Test: Crear una mesa correctamente"""
        self.assertEqual(self.mesa.numero, 1)
        self.assertEqual(self.mesa.capacidad, 4)
        self.assertEqual(self.mesa.ubicacion, 'salon_principal')
        self.assertEqual(self.mesa.estado, 'disponible')  # Estado por defecto
    
    def test_str_mesa(self):
        """Test: Representación en string de la mesa"""
        expected = "Mesa 1 - salon_principal (4 personas)"
        self.assertEqual(str(self.mesa), expected)
    
    def test_ubicacion_choices(self):
        """Test: Las ubicaciones están dentro de las opciones válidas"""
        ubicaciones_validas = ['salon_principal', 'terraza', 'vip', 'barra']
        self.assertIn(self.mesa.ubicacion, ubicaciones_validas)
    
    def test_estado_choices(self):
        """Test: Los estados son válidos"""
        estados_validos = ['disponible', 'ocupada', 'reservada', 'mantenimiento']
        self.assertIn(self.mesa.estado, estados_validos)
    
    def test_numero_unico(self):
        """Test: El número de mesa debe ser único"""
        with self.assertRaises(Exception):
            Mesa.objects.create(
                numero=1,  # Número duplicado
                capacidad=2,
                ubicacion='terraza'
            )


class ClienteModelTest(TestCase):
    """Tests para el modelo Cliente"""
    
    def setUp(self):
        """Configuración inicial"""
        self.cliente = Cliente.objects.create(
            nombre='Juan Pérez',
            telefono='+56912345678',
            email='juan@example.com',
            observaciones='Sin gluten'
        )
    
    def test_crear_cliente(self):
        """Test: Crear un cliente correctamente"""
        self.assertEqual(self.cliente.nombre, 'Juan Pérez')
        self.assertEqual(self.cliente.telefono, '+56912345678')
        self.assertEqual(self.cliente.email, 'juan@example.com')
        self.assertIsNotNone(self.cliente.fecha_registro)
    
    def test_str_cliente(self):
        """Test: Representación en string del cliente"""
        expected = "Juan Pérez - +56912345678"
        self.assertEqual(str(self.cliente), expected)
    
    def test_cliente_sin_telefono(self):
        """Test: Cliente puede crearse sin teléfono"""
        cliente = Cliente.objects.create(
            nombre='María López',
            email='maria@example.com'
        )
        self.assertIsNone(cliente.telefono)
        self.assertEqual(cliente.email, 'maria@example.com')


class ReservaModelTest(TestCase):
    """Tests para el modelo Reserva"""
    
    def setUp(self):
        """Configuración inicial"""
        self.mesa = Mesa.objects.create(
            numero=5,
            capacidad=6,
            ubicacion='terraza'
        )
        self.cliente = Cliente.objects.create(
            nombre='Carlos Soto',
            telefono='+56987654321'
        )
        self.user = User.objects.create_user(
            username='admin',
            password='admin123'
        )
        self.fecha_futura = datetime.now() + timedelta(days=2)
        self.reserva = Reserva.objects.create(
            cliente=self.cliente,
            mesa=self.mesa,
            fecha_reserva=self.fecha_futura,
            numero_personas=4,
            creada_por=self.user
        )
    
    def test_crear_reserva(self):
        """Test: Crear una reserva correctamente"""
        self.assertEqual(self.reserva.cliente, self.cliente)
        self.assertEqual(self.reserva.mesa, self.mesa)
        self.assertEqual(self.reserva.numero_personas, 4)
        self.assertEqual(self.reserva.estado, 'pendiente')  # Estado por defecto
    
    def test_str_reserva(self):
        """Test: Representación en string de la reserva"""
        self.assertIn('Mesa 5', str(self.reserva))
        self.assertIn('Carlos Soto', str(self.reserva))
    
    def test_relacion_cliente(self):
        """Test: Relación con cliente"""
        self.assertEqual(self.reserva.cliente.nombre, 'Carlos Soto')
        self.assertIn(self.reserva, self.cliente.reservas.all())
    
    def test_relacion_mesa(self):
        """Test: Relación con mesa"""
        self.assertEqual(self.reserva.mesa.numero, 5)
        self.assertIn(self.reserva, self.mesa.reservas.all())


class PedidoModelTest(TestCase):
    """Tests para el modelo Pedido"""
    
    def setUp(self):
        """Configuración inicial"""
        self.mesa = Mesa.objects.create(numero=10, capacidad=4, ubicacion='vip')
        self.cliente = Cliente.objects.create(nombre='Ana Torres', telefono='+56911111111')
        self.user = User.objects.create_user(username='mesero', password='mesero123')
        
        # Crear categoría e item
        self.categoria = CategoriaItem.objects.create(
            nombre='Platos Principales',
            descripcion='Comidas principales'
        )
        self.item = Item.objects.create(
            nombre='Lomo a lo pobre',
            descripcion='Lomo con papas fritas y huevo',
            categoria=self.categoria,
            precio=Decimal('12500'),
            disponible=True,
            tiempo_preparacion=25
        )
        
        self.pedido = Pedido.objects.create(
            mesa=self.mesa,
            cliente=self.cliente,
            atendido_por=self.user
        )
    
    def test_crear_pedido(self):
        """Test: Crear un pedido correctamente"""
        self.assertEqual(self.pedido.mesa, self.mesa)
        self.assertEqual(self.pedido.cliente, self.cliente)
        self.assertEqual(self.pedido.estado, 'pendiente')
        self.assertEqual(self.pedido.total, Decimal('0'))
    
    def test_agregar_detalle_pedido(self):
        """Test: Agregar items al pedido"""
        detalle = DetallePedido.objects.create(
            pedido=self.pedido,
            item=self.item,
            cantidad=2,
            precio_unitario=self.item.precio
        )
        self.assertEqual(detalle.cantidad, 2)
        self.assertEqual(detalle.subtotal, Decimal('25000'))  # 12500 * 2


# ============================================
# TESTS DE FORMULARIOS
# ============================================

class MesaFormTest(TestCase):
    """Tests para MesaForm"""
    
    def test_formulario_valido(self):
        """Test: Formulario con datos válidos"""
        form_data = {
            'numero': 15,
            'capacidad': 8,
            'ubicacion': 'terraza'
        }
        form = MesaForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_formulario_sin_numero(self):
        """Test: Formulario sin número es inválido"""
        form_data = {
            'capacidad': 4,
            'ubicacion': 'salon_principal'
        }
        form = MesaForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('numero', form.errors)
    
    def test_ubicacion_choices(self):
        """Test: Solo acepta ubicaciones válidas"""
        form = MesaForm()
        ubicaciones = [choice[0] for choice in form.fields['ubicacion'].choices]
        self.assertIn('salon_principal', ubicaciones)
        self.assertIn('terraza', ubicaciones)
        self.assertIn('vip', ubicaciones)
        self.assertIn('barra', ubicaciones)


class ClienteFormTest(TestCase):
    """Tests para ClienteForm"""
    
    def test_formulario_valido(self):
        """Test: Formulario con datos válidos"""
        form_data = {
            'nombre': 'Pedro González',
            'telefono': '+56922222222',
            'email': 'pedro@example.com',
            'observaciones': 'Alérgico a mariscos'
        }
        form = ClienteForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_formulario_solo_nombre(self):
        """Test: Cliente solo con nombre es válido"""
        form_data = {'nombre': 'Laura Díaz'}
        form = ClienteForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_formulario_sin_nombre(self):
        """Test: Sin nombre es inválido"""
        form_data = {'telefono': '+56933333333'}
        form = ClienteForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('nombre', form.errors)


class ReservaFormTest(TestCase):
    """Tests para ReservaForm"""
    
    def setUp(self):
        """Configuración inicial"""
        self.mesa = Mesa.objects.create(numero=20, capacidad=4, ubicacion='salon_principal')
        self.cliente = Cliente.objects.create(nombre='Test Cliente', telefono='+56944444444')
    
    def test_formulario_valido(self):
        """Test: Formulario de reserva válido"""
        fecha_futura = datetime.now() + timedelta(days=1)
        form_data = {
            'cliente': self.cliente.id,
            'mesa': self.mesa.id,
            'fecha_reserva': fecha_futura.strftime('%Y-%m-%dT%H:%M'),
            'numero_personas': 3,
            'estado': 'pendiente',
            'observaciones': 'Celebración de cumpleaños'
        }
        form = ReservaForm(data=form_data)
        self.assertTrue(form.is_valid())


# ============================================
# TESTS DE VISTAS
# ============================================

class MesaViewsTest(TestCase):
    """Tests para las vistas de Mesa"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = TestClient()
        self.mesa = Mesa.objects.create(numero=1, capacidad=4, ubicacion='salon_principal')
    
    def test_listar_mesas_view(self):
        """Test: Vista de lista de mesas"""
        response = self.client.get(reverse('listar_mesas'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mesa 1')
    
    def test_detalle_mesa_view(self):
        """Test: Vista de detalle de mesa"""
        response = self.client.get(reverse('ver_mesa', args=[self.mesa.pk]))
        self.assertEqual(response.status_code, 200)
        # Verificar que contiene información de la mesa
        self.assertContains(response, 'Mesa')
        self.assertContains(response, 'Disponible')
    
    def test_crear_mesa_view_get(self):
        """Test: Vista de creación de mesa (GET)"""
        response = self.client.get(reverse('crear_mesa'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')


class ClienteViewsTest(TestCase):
    """Tests para las vistas de Cliente"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = TestClient()
        self.cliente = Cliente.objects.create(
            nombre='Cliente Test',
            telefono='+56955555555'
        )
    
    def test_listar_clientes_view(self):
        """Test: Vista de lista de clientes"""
        response = self.client.get(reverse('listar_clientes'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cliente Test')
    
    def test_detalle_cliente_view(self):
        """Test: Vista de detalle de cliente"""
        response = self.client.get(reverse('ver_cliente', args=[self.cliente.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cliente Test')


# ============================================
# TESTS DE INTEGRACIÓN
# ============================================

class IntegracionReservaTest(TestCase):
    """Tests de integración para flujo completo de reserva"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = TestClient()
        self.user = User.objects.create_user(username='admin', password='admin123')
        self.mesa = Mesa.objects.create(numero=50, capacidad=6, ubicacion='terraza')
        self.cliente = Cliente.objects.create(
            nombre='Cliente Integración',
            telefono='+56966666666'
        )
    
    def test_flujo_completo_reserva(self):
        """Test: Flujo completo de crear una reserva"""
        # 1. Verificar que la mesa está disponible
        self.assertEqual(self.mesa.estado, 'disponible')
        
        # 2. Crear una reserva
        fecha_futura = datetime.now() + timedelta(days=3)
        reserva = Reserva.objects.create(
            cliente=self.cliente,
            mesa=self.mesa,
            fecha_reserva=fecha_futura,
            numero_personas=4,
            creada_por=self.user
        )
        
        # 3. Verificar que se creó correctamente
        self.assertEqual(reserva.estado, 'pendiente')
        self.assertEqual(reserva.numero_personas, 4)
        
        # 4. Confirmar la reserva
        reserva.estado = 'confirmada'
        reserva.save()
        self.assertEqual(reserva.estado, 'confirmada')
        
        # 5. Verificar que aparece en las reservas del cliente
        self.assertIn(reserva, self.cliente.reservas.all())