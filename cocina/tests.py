from django.test import TestCase, Client as TestClient
from django.urls import reverse
from decimal import Decimal
from .models import CategoriaPlato, Plato
from .forms import CategoriaPlatoForm, PlatoForm


# ============================================
# TESTS DE MODELOS
# ============================================

class CategoriaPlatoModelTest(TestCase):
    """Tests para el modelo CategoriaPlato"""
    
    def setUp(self):
        """Configuración inicial"""
        self.categoria = CategoriaPlato.objects.create(
            nombre='Entradas',
            descripcion='Platos de entrada y aperitivos'
        )
    
    def test_crear_categoria(self):
        """Test: Crear una categoría correctamente"""
        self.assertEqual(self.categoria.nombre, 'Entradas')
        self.assertEqual(self.categoria.descripcion, 'Platos de entrada y aperitivos')
    
    def test_str_categoria(self):
        """Test: Representación en string de la categoría"""
        self.assertEqual(str(self.categoria), 'Entradas')
    
    def test_categoria_sin_descripcion(self):
        """Test: Categoría puede crearse sin descripción"""
        categoria = CategoriaPlato.objects.create(nombre='Postres')
        self.assertEqual(categoria.nombre, 'Postres')
        self.assertTrue(categoria.descripcion == '' or categoria.descripcion is None)


class PlatoModelTest(TestCase):
    """Tests para el modelo Plato"""
    
    def setUp(self):
        """Configuración inicial"""
        self.categoria = CategoriaPlato.objects.create(
            nombre='Platos Principales',
            descripcion='Comidas principales'
        )
        self.plato = Plato.objects.create(
            nombre='Cazuela de Vacuno',
            descripcion='Cazuela tradicional chilena con carne de vacuno',
            categoria=self.categoria,
            precio=Decimal('8500'),
            disponible=True,
            tiempo_preparacion=30
        )
    
    def test_crear_plato(self):
        """Test: Crear un plato correctamente"""
        self.assertEqual(self.plato.nombre, 'Cazuela de Vacuno')
        self.assertEqual(self.plato.precio, Decimal('8500'))
        self.assertTrue(self.plato.disponible)
        self.assertEqual(self.plato.tiempo_preparacion, 30)
    
    def test_str_plato(self):
        """Test: Representación en string del plato"""
        # El __str__ del modelo incluye el precio
        self.assertIn('Cazuela de Vacuno', str(self.plato))
    
    def test_relacion_categoria(self):
        """Test: Relación con categoría"""
        self.assertEqual(self.plato.categoria, self.categoria)
        self.assertIn(self.plato, self.categoria.platos.all())
    
    def test_plato_disponible_por_defecto(self):
        """Test: Plato es disponible por defecto"""
        plato = Plato.objects.create(
            nombre='Pastel de Choclo',
            categoria=self.categoria,
            precio=Decimal('7500'),
            tiempo_preparacion=25
        )
        self.assertTrue(plato.disponible)
    
    def test_precio_decimal(self):
        """Test: El precio es un valor Decimal"""
        self.assertIsInstance(self.plato.precio, Decimal)
        self.assertGreater(self.plato.precio, 0)
    
    def test_plato_sin_categoria(self):
        """Test: Plato puede existir sin categoría (null=True)"""
        plato = Plato.objects.create(
            nombre='Plato Especial',
            descripcion='Sin categoría',
            precio=Decimal('10000'),
            tiempo_preparacion=20
        )
        self.assertIsNone(plato.categoria)


# ============================================
# TESTS DE FORMULARIOS
# ============================================

class CategoriaPlatoFormTest(TestCase):
    """Tests para CategoriaPlatoForm"""
    
    def test_formulario_valido(self):
        """Test: Formulario con datos válidos"""
        form_data = {
            'nombre': 'Bebidas',
            'descripcion': 'Todo tipo de bebidas'
        }
        form = CategoriaPlatoForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_formulario_sin_nombre(self):
        """Test: Formulario sin nombre es inválido"""
        form_data = {'descripcion': 'Descripción sin nombre'}
        form = CategoriaPlatoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('nombre', form.errors)
    
    def test_formulario_solo_nombre(self):
        """Test: Formulario solo con nombre es válido"""
        form_data = {'nombre': 'Sopas'}
        form = CategoriaPlatoForm(data=form_data)
        self.assertTrue(form.is_valid())


class PlatoFormTest(TestCase):
    """Tests para PlatoForm"""
    
    def setUp(self):
        """Configuración inicial"""
        self.categoria = CategoriaPlato.objects.create(nombre='Carnes')
    
    def test_formulario_valido(self):
        """Test: Formulario con datos válidos"""
        form_data = {
            'nombre': 'Bife Chorizo',
            'descripcion': 'Bife de chorizo a la parrilla',
            'categoria': self.categoria.id,
            'precio': '15000',
            'disponible': True,
            'tiempo_preparacion': 20
        }
        form = PlatoForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_formulario_sin_precio(self):
        """Test: Formulario sin precio es inválido"""
        form_data = {
            'nombre': 'Plato sin precio',
            'categoria': self.categoria.id,
            'tiempo_preparacion': 15
        }
        form = PlatoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('precio', form.errors)
    
    def test_formulario_precio_negativo(self):
        """Test: Precio negativo es inválido"""
        form_data = {
            'nombre': 'Plato',
            'precio': '-1000',
            'tiempo_preparacion': 10
        }
        form = PlatoForm(data=form_data)
        self.assertFalse(form.is_valid())


# ============================================
# TESTS DE VISTAS
# ============================================

class CocinaViewsTest(TestCase):
    """Tests para las vistas del módulo cocina"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = TestClient()
        self.categoria = CategoriaPlato.objects.create(
            nombre='Test Categoría',
            descripcion='Categoría de prueba'
        )
        self.plato = Plato.objects.create(
            nombre='Test Plato',
            descripcion='Plato de prueba',
            categoria=self.categoria,
            precio=Decimal('5000'),
            disponible=True,
            tiempo_preparacion=15
        )
    
    def test_cocina_index_view(self):
        """Test: Vista principal de cocina"""
        response = self.client.get('/cocina/')
        self.assertEqual(response.status_code, 200)
    
    def test_listar_platos_view(self):
        """Test: Vista de lista de platos"""
        response = self.client.get('/cocina/platos/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Plato')
    
    def test_detalle_plato_view(self):
        """Test: Vista de detalle de plato"""
        response = self.client.get(f'/cocina/platos/{self.plato.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Plato')
        self.assertContains(response, '5000')
    
    def test_listar_categorias_view(self):
        """Test: Vista de lista de categorías"""
        response = self.client.get('/cocina/categorias/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Categoría')
    
    def test_crear_categoria_view_get(self):
        """Test: Vista de creación de categoría (GET)"""
        response = self.client.get('/cocina/categorias/crear/')
        self.assertEqual(response.status_code, 200)
    
    def test_crear_plato_view_get(self):
        """Test: Vista de creación de plato (GET)"""
        response = self.client.get('/cocina/platos/crear/')
        self.assertEqual(response.status_code, 200)


# ============================================
# TESTS DE FILTROS
# ============================================

class FiltrosPlatosTest(TestCase):
    """Tests para los filtros de platos"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = TestClient()
        self.categoria1 = CategoriaPlato.objects.create(nombre='Entradas')
        self.categoria2 = CategoriaPlato.objects.create(nombre='Postres')
        
        self.plato_disponible = Plato.objects.create(
            nombre='Plato Disponible',
            categoria=self.categoria1,
            precio=Decimal('6000'),
            disponible=True,
            tiempo_preparacion=10
        )
        
        self.plato_no_disponible = Plato.objects.create(
            nombre='Plato No Disponible',
            categoria=self.categoria2,
            precio=Decimal('7000'),
            disponible=False,
            tiempo_preparacion=15
        )
    
    def test_filtrar_por_disponibilidad(self):
        """Test: Filtrar platos disponibles"""
        response = self.client.get('/cocina/platos/?disponible=true')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Plato Disponible')
    
    def test_filtrar_por_categoria(self):
        """Test: Filtrar platos por categoría"""
        response = self.client.get(f'/cocina/platos/?categoria={self.categoria1.id}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Plato Disponible')


# ============================================
# TESTS DE INTEGRACIÓN
# ============================================

class IntegracionCocinaTest(TestCase):
    """Tests de integración para el módulo cocina"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = TestClient()
    
    def test_flujo_completo_creacion_plato(self):
        """Test: Flujo completo de crear categoría y plato"""
        # 1. Crear una categoría
        categoria = CategoriaPlato.objects.create(
            nombre='Ensaladas',
            descripcion='Ensaladas frescas'
        )
        self.assertEqual(CategoriaPlato.objects.count(), 1)
        
        # 2. Crear un plato en esa categoría
        plato = Plato.objects.create(
            nombre='Ensalada César',
            descripcion='Ensalada clásica con pollo',
            categoria=categoria,
            precio=Decimal('6500'),
            disponible=True,
            tiempo_preparacion=10
        )
        
        # 3. Verificar relación
        self.assertEqual(plato.categoria, categoria)
        self.assertEqual(categoria.platos.count(), 1)
        
        # 4. Cambiar disponibilidad
        plato.disponible = False
        plato.save()
        self.assertFalse(plato.disponible)
        
        # 5. Verificar que se puede recuperar
        plato_db = Plato.objects.get(nombre='Ensalada César')
        self.assertEqual(plato_db.precio, Decimal('6500'))
        self.assertFalse(plato_db.disponible)
